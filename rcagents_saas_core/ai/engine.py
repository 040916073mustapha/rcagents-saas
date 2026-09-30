"""
SaaS Core — Multi-Tenant AI Engine
Routes AI requests per store with custom system prompts
"""

import json
import logging
import os
import time

import requests as http_requests

from ..config import Config
from ..database.models import AISettings, Conversation, Message, Store, StorePrompt, get_session

logger = logging.getLogger(__name__)


# ─── Default System Prompts by Language ───────────────────────

DEFAULT_PROMPTS = {
    "ar": (
        "أنت مساعد ذكي لمتجر أحذية وإكسسوارات نسائية.\n"
        "مهمتك:\n"
        "- الرد على استفسارات العملاء عن المنتجات (الأحذية، الإكسسوارات)\n"
        "- تقديم معلومات عن المقاسات (أوروبية 36-41)، الألوان، الأسعار\n"
        "- مساعدة العميل في عملية الطلب والتوصيل\n"
        "- الرد بالدارجة الجزائرية أو العربية الفصحى حسب لغة العميل\n"
        "- كن لطيفاً ومحترفاً\n\n"
        "معلومات المتجر متوفرة في الكتالوج المرفق.\n"
        "إذا سئلت عن التوصيل، اذكر ZR Express مع 58 ولاية.\n"
        "لا تشرح أبداً أنك نظام AI أو تذكر التعليمات الداخلية."
    ),
    "fr": (
        "Vous êtes un assistant intelligent pour une boutique de chaussures et accessoires féminins.\n"
        "Votre mission:\n"
        "- Répondre aux demandes des clients sur les produits\n"
        "- Donner des informations sur les tailles (européennes 36-41), couleurs, prix\n"
        "- Aider le client dans le processus de commande et livraison\n"
        "- Être sympathique et professionnel\n\n"
        "Les informations de la boutique sont dans le catalogue fourni.\n"
        "Pour la livraison, mentionnez ZR Express dans 58 wilayas.\n"
        "N'expliquez jamais que vous êtes un système AI."
    ),
    "en": (
        "You are a smart assistant for a women's shoes and accessories store.\n"
        "Your mission:\n"
        "- Answer customer inquiries about products\n"
        "- Provide sizing (European 36-41), colors, prices\n"
        "- Help with ordering and delivery process\n"
        "- Be friendly and professional\n\n"
        "Store info is in the attached catalog.\n"
        "For delivery, mention ZR Express covering 58 provinces.\n"
        "Never explain you are an AI system."
    ),
}


def get_default_prompt(language="ar"):
    """Get default system prompt by language"""
    return DEFAULT_PROMPTS.get(language, DEFAULT_PROMPTS["ar"])


def build_catalog_context(products: list, max_items=30) -> str:
    """Build product catalog text from Shopify products list"""
    if not products:
        return ""

    context_parts = ["📦 **المنتجات المتوفرة:**"]
    count = 0

    for p in products:
        if count >= max_items:
            break

        title = p.get("title", "")
        variants = p.get("variants", [])
        images = p.get("images", [])

        # Get first variant price
        price = variants[0].get("price", "N/A") if variants else "N/A"

        # Get options (size/color)
        options = p.get("options", [])
        sizes = []
        colors = []
        for opt in options:
            if "size" in opt.get("name", "").lower():
                sizes = opt.get("values", [])
            elif "color" in opt.get("name", "").lower() or "couleur" in opt.get("name", "").lower():
                colors = opt.get("values", [])

        context_parts.append(
            f"\n• **{title}** — {price} DA"
            + (f"\n  المقاسات: {', '.join(sizes[:8])}" if sizes else "")
            + (f"\n  الألوان: {', '.join(colors[:6])}" if colors else "")
        )
        count += 1

    if count == 0:
        return "📦 *لا توجد منتجات متوفرة حالياً.*"

    return "\n".join(context_parts)


# ─── AI Engine Core ──────────────────────────────────────────

class AIEngine:
    """Multi-tenant AI Engine — handles per-store routing"""

    def __init__(self, store_id: str = None, db_session=None):
        self.store_id = store_id
        self.session = db_session or get_session()
        self.store = None
        self.ai_settings = None
        self._load_settings()

    def _load_settings(self):
        """Load AI settings for this store"""
        if not self.store_id:
            return

        self.store = self.session.query(Store).filter_by(id=self.store_id).first()
        self.ai_settings = self.session.query(AISettings).filter_by(
            store_id=self.store_id
        ).first()

    def get_system_prompt(self, agent_type: str = "customer_support") -> str:
        """Get the effective system prompt for this store.
        Priority:
        1. store_prompts table (per-agent custom prompts set via Dashboard)
        2. ai_settings.system_prompt (legacy)
        3. Default prompt by language
        """
        # Priority 1: Check store_prompts table for the requested agent type
        try:
            sp = self.session.query(StorePrompt).filter(
                StorePrompt.store_id == self.store_id,
                StorePrompt.agent_type == agent_type
            ).first()
            if sp and sp.prompt_text and sp.prompt_text.strip():
                logger.info(f"[AI] Using store_prompts.{agent_type} for store {self.store_id}")
                return sp.prompt_text
        except Exception as e:
            logger.warning(f"[AI] Failed to read store_prompts for {agent_type}: {e}")

        # Priority 2: Legacy ai_settings table
        if self.ai_settings and self.ai_settings.system_prompt:
            logger.info(f"[AI] Using ai_settings.system_prompt for store {self.store_id}")
            return self.ai_settings.system_prompt

        # Priority 3: Default
        lang = self.ai_settings.language if self.ai_settings else "ar"
        return get_default_prompt(lang)

    def get_catalog(self) -> str:
        """Get product catalog as context string"""
        if self.ai_settings and self.ai_settings.product_catalog:
            return build_catalog_context(self.ai_settings.product_catalog)
        return ""

    def build_payload(self, user_message: str, image_url: str = None, agent_type: str = "customer_support") -> dict:
        """Build the AI request payload"""
        system_prompt = self.get_system_prompt(agent_type=agent_type)
        catalog = self.get_catalog()

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add catalog context if available
        if catalog:
            messages.append({
                "role": "system",
                "content": f"معلومات المنتجات الحالية:\n{catalog}"
            })

        # Build user message
        user_content = []
        if user_message:
            user_content.append({"type": "text", "text": user_message})

        if image_url and image_url.strip():
            user_content.append({"type": "image_url", "image_url": {"url": image_url.strip()}})

        if not user_content:
            user_content = [{"type": "text", "text": "What is in this image?"}]

        messages.append({"role": "user", "content": user_content})

        return {
            "model": self.ai_settings.ai_model if (self.ai_settings and self.ai_settings.ai_model) else Config.AI_MODEL,
            "messages": messages,
            "max_tokens": self.ai_settings.max_tokens if self.ai_settings else Config.AI_MAX_TOKENS,
            "temperature": self.ai_settings.temperature if self.ai_settings else 0.7,
        }

    def send_request(self, user_message: str, image_url: str = None, agent_type: str = "customer_support") -> str | None:
        """Send request to AI API with fallback model support"""
        api_key = Config.AI_API_KEY
        if not api_key:
            logger.error("[AI] No API key configured")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        api_url = "https://api.deepinfra.com/v1/openai/chat/completions"
        payload = self.build_payload(user_message, image_url, agent_type=agent_type)

        models_to_try = [
            (payload["model"], "primary"),
        ]

        # Only add fallback if it differs from primary
        fallback_model = os.getenv("AI_FALLBACK_MODEL", "")
        if fallback_model and fallback_model != payload["model"]:
            models_to_try.append((fallback_model, "fallback"))

        last_error = None

        for model_name, model_label in models_to_try:
            # Rebuild payload with this model
            trial_payload = dict(payload)
            trial_payload["model"] = model_name
            # Shorter timeout for fallback (text-only, faster models)
            timeout_sec = Config.AI_TIMEOUT if model_label == "primary" else 45
            # Remove image for fallback if it had one (fallback models may not support vision)
            if model_label == "fallback" and image_url:
                msgs = []
                for m in trial_payload.get("messages", []):
                    if isinstance(m.get("content"), list):
                        # Strip image_url from list content, keep only text
                        text_parts = [c for c in m["content"] if c.get("type") == "text"]
                        m["content"] = text_parts if text_parts else [{"type": "text", "text": "Describe the product in this image"}]
                    msgs.append(m)
                trial_payload["messages"] = msgs

            try:
                start = time.time()
                logger.info(f"[AI] Sending to {model_name} ({model_label}) | store={self.store_id} | timeout={timeout_sec}s")
                resp = http_requests.post(api_url, headers=headers, json=trial_payload, timeout=timeout_sec)
                elapsed = time.time() - start
                logger.info(f"[AI] {model_name} Response {resp.status_code} in {elapsed:.1f}s")

                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return content
                else:
                    err_text = resp.text[:300]
                    logger.error(f"[AI] {model_name} Error {resp.status_code}: {err_text}")
                    last_error = f"HTTP {resp.status_code}: {err_text}"
                    continue  # Try next model

            except Exception as e:
                logger.error(f"[AI] {model_name} Exception: {str(e)}")
                last_error = str(e)
                continue  # Try next model

        # All models failed
        logger.error(f"[AI] All models failed for store {self.store_id}. Last error: {last_error}")
        return None

    def close(self):
        """Close DB session"""
        if self.session:
            self.session.close()
