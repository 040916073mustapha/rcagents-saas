"""
RC Agents — SaaS Core Backend (Multi-Tenant)
Flask application entry point
Uses relative imports only — clean, works from any context
"""

import os
import sys
import logging

# Add parent directory to path (works for both run_saas.py and direct execution)
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

import hashlib
import hmac
import uuid

from flask import Flask, jsonify, send_from_directory, request, Response, render_template
from flask_cors import CORS

from .config import Config
from .database.models import init_db

# Import API Blueprints
from .api.auth import auth_bp
from .api.stores import stores_bp
from .api.settings import settings_bp
from .api.conversations import conversations_bp
from .api.zr_express import zr_bp
from .api.stats import stats_bp

# ─── Logging ──────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("saas-core")


# ─── App Factory ──────────────────────────────────────────────

def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")

    # CORS — allow all origins during development
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(stores_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(zr_bp)
    app.register_blueprint(stats_bp)

    # Configure template folder for Dark Neon Dashboard
    _template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "templates")
    if os.path.isdir(_template_dir):
        app.template_folder = _template_dir
        app.jinja_loader = __import__("jinja2").FileSystemLoader(_template_dir)
        app.logger.info(f"Using template folder: {_template_dir}")

    # ─── Init Database ────────────────────────────────────────
    with app.app_context():
        try:
            engine = init_db()
            logger.info("✅ Database initialized successfully")
            # Seed default AI settings for store=1 (legacy compatibility)
            try:
                from sqlalchemy import text as _sql_text
                from datetime import datetime as _dt
                with engine.connect() as _conn:
                    _existing = _conn.execute(_sql_text("SELECT id, ai_model, system_prompt FROM ai_settings WHERE store_id = '1'")).fetchone()
                    _DEFAULT_PROMPT = ("[1. ROYAL IDENTITY]\nName: Louve\nRole: Sales assistant\nStore: Royal Chaussures\n\n[2. RULES]\n- Reply in Algerian Arabic\n- Use emojis\n- Never say you are AI\n\n[3. PRODUCTS]\n- Sizes: 36-41 EU\n- Delivery: ZR Express all Algeria\n- Payment: Cash on delivery")
                    if _existing:
                        _needs_update = not _existing[1] or not _existing[2]
                        if _needs_update:
                            _conn.execute(
                                _sql_text("UPDATE ai_settings SET ai_model = 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', system_prompt = :prompt, language = 'ar', temperature = 0.7, max_tokens = 2048, greeting_enabled = TRUE, updated_at = :now WHERE store_id = '1'"),
                                {"prompt": _DEFAULT_PROMPT, "now": _dt.utcnow()}
                            )
                            _conn.commit()
                            logger.info("✅ AI settings updated for store 1 (model + prompt)")
                        else:
                            logger.info("✅ AI settings for store 1 already configured")
                    else:
                        _conn.execute(
                            _sql_text("INSERT INTO ai_settings (id, store_id, ai_model, system_prompt, language, temperature, max_tokens, greeting_enabled) VALUES (gen_random_uuid()::text, '1', 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', :prompt, 'ar', 0.7, 2048, TRUE)"),
                            {"prompt": _DEFAULT_PROMPT}
                        )
                        _conn.commit()
                        logger.info("✅ AI settings created for store 1")
            except Exception as ai_e:
                logger.warning(f"⚠️ AI settings seed (non-critical): {ai_e}")
        except Exception as e:
            logger.warning(f"⚠️ DB init (will retry on first request): {e}")

    # ─── Routes ────────────────────────────────────────────────

    @app.route("/")
    def index():
        """Landing Page — the main entrance to RC Agents"""
        try:
            return render_template("landing.html")
        except Exception:
            return send_from_directory(app.static_folder, "landing.html")

    @app.route("/dashboard")
    def dashboard():
        """Dark Neon Cyberpunk Dashboard — full with AI Brain + Charts + Live Chat"""
        try:
            return render_template("dashboard.html")
        except Exception:
            try:
                return render_template("dashboard_base.html")
            except Exception:
                return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/onboard")
    def onboard():
        """Onboarding / Sign-Up page"""
        try:
            return render_template("onboard.html")
        except Exception:
            return send_from_directory(app.static_folder, "onboard.html")

    @app.route("/login")
    def login():
        """Login page"""
        try:
            return render_template("dashboard_login.html")
        except Exception:
            return send_from_directory(app.static_folder, "dashboard_login.html")

    @app.route("/privacy")
    def privacy():
        """Privacy Policy — required for Meta App Review"""
        try:
            return render_template("privacy.html")
        except Exception:
            return send_from_directory(app.static_folder, "privacy.html")

    @app.route("/data-deletion")
    def data_deletion():
        """Data Deletion Instructions — required for Meta App Review"""
        try:
            return render_template("data_deletion.html")
        except Exception:
            return send_from_directory(app.static_folder, "data_deletion.html")

    @app.route("/terms")
    def terms():
        """Terms of Service — required for Meta App Review"""
        try:
            return render_template("terms.html")
        except Exception:
            return send_from_directory(app.static_folder, "terms.html")

    @app.route("/dashboard/orders")
    def dashboard_orders():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/clients")
    def dashboard_clients():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/products")
    def dashboard_products():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/chat")
    def dashboard_chat():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/settings")
    def dashboard_settings():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/shipments")
    def dashboard_shipments():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/constellation")
    def dashboard_constellation():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/auto-ship")
    def dashboard_autoship():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/agents")
    def dashboard_agents():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/analytics")
    def dashboard_analytics():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/inventory")
    def dashboard_inventory():
        return send_from_directory(app.static_folder, "dashboard.html")

    @app.route("/dashboard/marketing")
    def dashboard_marketing():
        return send_from_directory(app.static_folder, "dashboard.html")

    # ─── Webhook Endpoint (Messenger & Instagram) with HMAC-SHA256 ──

    META_APP_SECRET = os.getenv("META_APP_SECRET", "")

    def _verify_webhook_signature(request_body, signature_header):
        """Verify X-Hub-Signature-256 against request body"""
        if not META_APP_SECRET or not signature_header:
            return True  # soft pass if not configured
        try:
            expected = "sha256=" + hmac.new(
                META_APP_SECRET.encode("utf-8"),
                request_body,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected, signature_header)
        except Exception as e:
            logger.warning(f"[WEBHOOK] HMAC error: {e}")
            return True

    FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "ROYAL-ROYAL-CH2026")

    @app.route("/webhook", methods=["GET", "POST"])
    def webhook():
        # GET: Facebook verification challenge
        if request.method == "GET":
            mode = request.args.get("hub.mode")
            token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")
            logger.info(f"Webhook GET: mode={mode}")
            if mode == "subscribe" and token == FB_VERIFY_TOKEN:
                logger.info("Webhook verified!")
                return Response(challenge, status=200, content_type="text/plain")
            logger.warning("Webhook verify failed")
            return "Verification failed", 403

        # POST: Process incoming message with HMAC verification
        logger.info("Webhook POST received")

        # Verify X-Hub-Signature-256
        signature = request.headers.get("X-Hub-Signature-256", "")
        raw_body = request.get_data()
        if not _verify_webhook_signature(raw_body, signature):
            logger.warning(f"[WEBHOOK] Invalid signature! Possible tampering.")
            return jsonify({"status": "signature_mismatch"}), 403

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "ok"})

        obj = data.get("object", "")
        logger.info(f"Webhook object={obj}")

        if obj == "page":
            _process_messaging_multi(data.get("entry", []), "FB", _send_fb_reply_ai)
        elif obj == "instagram":
            _process_messaging_multi(data.get("entry", []), "IG", _send_ig_reply_ai)
        elif obj == "whatsapp_business_account":
            _process_whatsapp_multi(data.get("entry", []))
        else:
            logger.warning(f"Unknown webhook object: {obj}")

        return jsonify({"status": "ok"})

    @app.route("/webhook/", methods=["GET", "POST"])
    def webhook_slash():
        return webhook()

    @app.route("/whatsapp/webhook", methods=["GET", "POST"])
    def whatsapp_webhook():
        if request.method == "GET":
            mode = request.args.get("hub.mode")
            token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")
            if mode == "subscribe" and token == FB_VERIFY_TOKEN:
                return Response(challenge, status=200, content_type="text/plain")
            return "Verification failed", 403

        data = request.get_json(silent=True)
        if data:
            logger.info(f"WhatsApp webhook received")
            _process_whatsapp_multi(data.get("entry", []))
        return jsonify({"status": "ok"})

    # ─── AI Engine + Platform Senders (standalone, no server.py) ──
    import threading as _th
    import requests as _http

    # Load FB/WA tokens from env
    _FB_PAGE_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    _WA_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    _WA_PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    _META_API = "https://graph.facebook.com/v21.0"

    # ─── Deduplication set (tracks processed message mids) ──
    __processed_mids = set()

    # ─── Startup Environment Validation ────────────────────
    _missing_env = []
    if not _FB_PAGE_TOKEN:
        _missing_env.append("FACEBOOK_PAGE_ACCESS_TOKEN")
    if not _WA_TOKEN:
        _missing_env.append("WHATSAPP_ACCESS_TOKEN")
    if not _WA_PHONE_ID:
        _missing_env.append("WHATSAPP_PHONE_NUMBER_ID")
    ig_id_check = os.getenv("INSTAGRAM_BUSINESS_ID", "")
    if not ig_id_check:
        _missing_env.append("INSTAGRAM_BUSINESS_ID")
    if _missing_env:
        logger.warning(f"⚠️ STARTUP: Missing env vars — {', '.join(_missing_env)}. Bot replies will FAIL for these channels!")
    else:
        logger.info("✅ STARTUP: All Meta env vars present (FB, WA, IG)")

    def _call_ai_and_save(store_id, sender_id, user_text, image_url, channel_type, platform):
        """Core: call AIEngine, save reply, return reply text or None"""
        from .ai.engine import AIEngine
        ai = AIEngine(store_id)
        ai_reply = None
        try:
            # Use 'customer_support' as the default agent type for webhook replies
            # The prompt is now fetched from store_prompts table (set via Dashboard AI Agents Editor)
            ai_reply = ai.send_request(user_text, image_url, agent_type="customer_support")
        except Exception as e:
            logger.error(f"[AI] Engine error for store {store_id}: {e}")
        finally:
            ai.close()

        # Fallback reply if AI failed or timed out
        if not ai_reply:
            ai_reply = "عذراً، لدينا بعض المشاكل التقنية حالياً. يمكنك التواصل معنا على الرقم +213659832426 🙏"
            logger.info(f"[AI] Using fallback reply for {platform}/{sender_id[:20]}")

        # Save to DB inside try/except so a DB error never blocks sending
        try:
            from .database.crud import get_or_create_conversation, save_message
            conv = get_or_create_conversation(store_id, channel_type, sender_id, customer_platform_id=sender_id)
            save_message(conv.id, store_id, "assistant", ai_reply, channel_type, "text")
        except Exception as e:
            logger.error(f"[DB] Failed to save message for {platform}/{sender_id[:20]}: {e}")

        logger.info(f"[AI] Reply ready for {platform}/{sender_id[:20]}: '{ai_reply[:80]}...' store={store_id}")
        return ai_reply

    def _send_fb_reply_ai(sender_id, text, image_url, store_id):
        """Messenger: AI reply + send via Graph API with response logging"""
        reply = _call_ai_and_save(store_id, sender_id, text, image_url, "messenger", "FB")
        if not reply:
            logger.error(f"[FB] No reply text to send to {sender_id[:20]}")
            return
        if not _FB_PAGE_TOKEN:
            logger.error(f"[FB] FACEBOOK_PAGE_ACCESS_TOKEN is empty — cannot send")
            return
        try:
            logger.info(f"[FB] Sending to {sender_id[:20]}...")
            resp = _http.post(
                f"{_META_API}/me/messages",
                params={"access_token": _FB_PAGE_TOKEN},
                json={"recipient": {"id": sender_id}, "message": {"text": reply[:2000]}},
                timeout=15
            )
            logger.info(f"[FB] Response {resp.status_code}: {resp.text[:200]}")
            if resp.status_code != 200:
                logger.error(f"[FB] Meta API error: {resp.status_code} {resp.text[:300]}")
        except Exception as e:
            logger.error(f"[FB] Send error: {e}")

    def _send_ig_reply_ai(sender_id, text, image_url, store_id):
        """Instagram: AI reply + send via Graph API with response logging.
        Uses /me/messages (Page Access Token) — the same endpoint as FB Messenger.
        Instagram DM replies are routed through the Page, not the IG Business Account ID."""
        reply = _call_ai_and_save(store_id, sender_id, text, image_url, "instagram", "IG")
        if not reply:
            logger.error(f"[IG] No reply text to send to {sender_id[:20]}")
            return
        if not _FB_PAGE_TOKEN:
            logger.error(f"[IG] FACEBOOK_PAGE_ACCESS_TOKEN is empty — cannot send")
            return
        try:
            logger.info(f"[IG] Sending to {sender_id[:20]} via /me/messages (Page Token)...")
            resp = _http.post(
                f"{_META_API}/me/messages",
                params={"access_token": _FB_PAGE_TOKEN},
                json={"recipient": {"id": sender_id}, "message": {"text": reply[:2000]}},
                timeout=15
            )
            logger.info(f"[IG] Response {resp.status_code}: {resp.text[:200]}")
            if resp.status_code != 200:
                logger.error(f"[IG] Meta API error: {resp.status_code} {resp.text[:300]}")
        except Exception as e:
            logger.error(f"[IG] Send error: {e}")

    def _send_wa_reply_ai(sender_id, text, image_url, store_id):
        """WhatsApp: AI reply + send via Graph API with response logging"""
        reply = _call_ai_and_save(store_id, sender_id, text, image_url, "whatsapp", "WA")
        if not reply:
            logger.error(f"[WA] No reply text to send to {sender_id[:20]}")
            return
        if not _WA_TOKEN or not _WA_PHONE_ID:
            logger.error(f"[WA] Missing token or phone ID — cannot send")
            return
        try:
            logger.info(f"[WA] Sending to {sender_id[:20]}...")
            resp = _http.post(
                f"{_META_API}/{_WA_PHONE_ID}/messages",
                headers={"Authorization": f"Bearer {_WA_TOKEN}"},
                json={"messaging_product": "whatsapp", "to": sender_id, "text": {"body": reply[:4096]}},
                timeout=15
            )
            logger.info(f"[WA] Response {resp.status_code}: {resp.text[:200]}")
            if resp.status_code != 200:
                logger.error(f"[WA] Meta API error: {resp.status_code} {resp.text[:300]}")
        except Exception as e:
            logger.error(f"[WA] Send error: {e}")

    # ─── Multi-Tenant Webhook Processors ─────────────────────

    from .database.crud import get_store_id_by_platform as _saas_get_store_id, get_store_id_by_whatsapp_phone as _saas_get_store_wa, get_or_create_conversation, save_message

    def _get_store_id_from_entry(entry, channel_type):
        """Extract store_id from webhook entry based on channel type.
        Falls back to store_id='1' for legacy single-store setup (Royal Chaussures)."""
        entry_id = entry.get("id", "")
        if entry_id:
            try:
                sid = _saas_get_store_id(channel_type, str(entry_id))
                if sid:
                    return sid
            except Exception:
                pass
        # Fallback to default store (Royal Chaussures) for single-tenant legacy mode
        logger.info(f"[MT] No channel registered for {channel_type}/{entry_id}, falling back to store_id=1")
        return "1"

    def _process_messaging_multi(entries, platform, send_func):
        """Multi-tenant: process Messenger/Instagram messages with store_id lookup"""
        logger.info(f"[MT] process_messaging: plat={platform} entries={len(entries)}")
        channel_type = "messenger" if platform == "FB" else "instagram"
        for entry in entries:
            store_id = _get_store_id_from_entry(entry, channel_type)
            if not store_id:
                logger.warning(f"[MT] No store for {channel_type} entry {entry.get('id','')}, skipping")
                continue
            for messaging in entry.get("messaging", []):
                sid = messaging.get("sender", {}).get("id", "")
                msg_data = messaging.get("message", {})
                # ─── Skip echo (bot's own replies) ───────────────
                if msg_data.get("is_echo", False):
                    logger.info(f"[ECHO] Skipping echo message from {sid[:20]} (bot's own reply)")
                    continue
                # Deduplicate by message.mid
                mid = msg_data.get("mid", "")
                if mid:
                    if mid in __processed_mids:
                        logger.info(f"[DEDUP] Skipping duplicate mid={mid[:20]}...")
                        continue
                    __processed_mids.add(mid)
                # Keep set bounded (prevent memory leak)
                if len(__processed_mids) > 2000:
                    __processed_mids.clear()
                text = msg_data.get("text", "") or ""
                image_url = ""
                attachments = msg_data.get("attachments", [])
                if attachments:
                    for att in attachments:
                        if att.get("type") == "image":
                            payload = att.get("payload") or {}
                            image_url = payload.get("url") or att.get("url") or ""
                            if image_url:
                                break
                image_url = image_url or ""
                if sid and (text or image_url):
                    try:
                        conv = get_or_create_conversation(store_id, channel_type, sid, customer_platform_id=sid)
                        save_message(conv.id, store_id, "user", text or "[Image]", channel_type, "image" if image_url else "text", image_url)
                        logger.info(f"[MT] {platform} msg from {sid}: text='{text[:60]}' store={store_id}")
                        # Fire AI reply in background thread
                        _th.Thread(target=send_func, args=(sid, text, image_url, store_id), daemon=True).start()
                    except Exception as msg_e:
                        logger.error(f"[MT] Error processing message: {msg_e}")

    def _process_whatsapp_multi(entries):
        """Multi-tenant: process WhatsApp messages with store_id lookup"""
        logger.info(f"[MT] process_whatsapp: entries={len(entries)}")
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                metadata = value.get("metadata", {})
                phone_id = metadata.get("phone_number_id", "")
                store_id = None
                if phone_id:
                    try:
                        store_id = _saas_get_store_wa(str(phone_id))
                    except Exception:
                        pass
                if not store_id:
                    logger.info(f"[MT] No store for WA phone {phone_id}, falling back to store_id=1")
                    store_id = "1"
                for msg in value.get("messages", []):
                    # Deduplicate WhatsApp by wamid
                    wamid = msg.get("id", "")
                    if wamid:
                        if wamid in __processed_mids:
                            logger.info(f"[DEDUP] WA skipping duplicate wamid={wamid[:20]}...")
                            continue
                        __processed_mids.add(wamid)
                    # ─── Skip WA echo from bot own number ─────────
                    if msg.get("statuses") or msg.get("errors") or msg.get("context", {}).get("from", "") == _WA_PHONE_ID or msg.get("from", "") == _WA_PHONE_ID:
                        continue
                    sender = msg.get("from", "")
                    text = (msg.get("text") or {}).get("body", "") or ""
                    img = msg.get("image") or {}
                    image_url = img.get("id") or img.get("link") or ""
                    if sender and (text or image_url):
                        try:
                            conv = get_or_create_conversation(store_id, "whatsapp", sender, customer_platform_id=sender)
                            save_message(conv.id, store_id, "user", text or "[Image]", "whatsapp", "image" if image_url else "text", image_url)
                            logger.info(f"[MT] WA msg from {sender}: text='{text[:60]}' store={store_id}")
                            _th.Thread(target=_send_wa_reply_ai, args=(sender, text, image_url, store_id), daemon=True).start()
                        except Exception as msg_e:
                            logger.error(f"[MT] WA error: {msg_e}")

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "rc-agents-saas-core",
            "version": "2.1.0",
            "ai_model": os.getenv("AI_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"),
        })

    @app.route("/api/plans")
    def list_plans():
        return jsonify(Config.PLANS)

    # ─── API: Tenant Onboard (Multi-Store Registration) ──────

    @app.route("/api/tenant/onboard", methods=["POST"])
    def tenant_onboard():
        """Register a new store/tenant"""
        try:
            data = request.get_json(force=True)
            store_name = data.get("store_name", "").strip()
            email = data.get("email", "").strip()
            phone = data.get("phone", "").strip()
            username = data.get("username", "").strip()
            password = data.get("password", "")
            webhooks = data.get("webhooks", {})

            if not store_name or not username or not password:
                return jsonify({"success": False, "error": "store_name, username, and password are required"}), 400
            if len(password) < 6:
                return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400

            store_id = str(uuid.uuid4())[:8]
            slug = store_name.lower().replace(" ", "-").replace("'", "")[:20]

            # Simple in-memory registration for now (DB persistence in next iteration)
            _tenant_registry = getattr(app, "_tenant_registry", {})
            _tenant_registry[store_id] = {
                "store_name": store_name,
                "email": email,
                "phone": phone,
                "username": username,
                "password": password,
                "webhooks": webhooks,
                "slug": slug,
                "store_id": store_id,
            }
            app._tenant_registry = _tenant_registry

            logger.info(f"✅ New tenant registered: {store_name} (ID: {store_id})")

            return jsonify({
                "success": True,
                "store_name": store_name,
                "store_id": store_id,
                "slug": slug,
                "username": username,
                "subdomain": f"{slug}.rcagents.space",
            })
        except Exception as e:
            logger.error(f"Tenant onboard error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/tenant/test-shopify", methods=["POST"])
    def test_shopify_connection():
        """Test Shopify connection with provided credentials"""
        try:
            data = request.get_json(force=True)
            domain = data.get("shopify_domain", "").strip()
            token = data.get("shopify_token", "").strip()

            if not domain or not token:
                return jsonify({"success": False, "error": "Domain and token required"}), 400

            # Mock connection for demo store
            if 'rwqchh-na' in domain and 'shpat_' in token:
                logger.info(f"✅ Mock Shopify connection for demo store: {domain}")
                return jsonify({
                    "success": True,
                    "products": 8,
                    "store_name": "Royal Chaussures"
                })

            import requests as _req
            url = f"https://{domain}/admin/api/2024-10/products.json?limit=1"
            headers = {
                "X-Shopify-Access-Token": token,
                "Content-Type": "application/json"
            }
            resp = _req.get(url, headers=headers, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                products = data.get("products", [])
                return jsonify({
                    "success": True,
                    "products": len(products),
                    "store_name": domain.split(".")[0]
                })
            elif resp.status_code == 401:
                return jsonify({"success": False, "error": "Invalid API token (401)"}), 401
            else:
                return jsonify({"success": False, "error": f"Shopify returned {resp.status_code}"}), resp.status_code

        except Exception as e:
            logger.error(f"Test Shopify error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ─── Error Handlers ──────────────────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"500 error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/api/admin/migrate")
    def api_migrate():
        """Run DB migration + seed AI settings for store 1"""
        _seed_result = "skipped"
        try:
            from .database.models import Base, get_engine
            from sqlalchemy import text as _txt
            from datetime import datetime as _dt
            import uuid
            url = os.getenv("DATABASE_URL") or os.getenv("SAAS_DATABASE_URL")
            if not url:
                return jsonify({"error": "No DATABASE_URL in environment"}), 400
            engine = get_engine(url)
            Base.metadata.create_all(engine)
            inspector = __import__("sqlalchemy").inspect(engine)
            tables = inspector.get_table_names()

            # Seed AI settings for store=1
            try:
                _ai_prompt = "[1. ROYAL IDENTITY]\nName: Louve\nRole: Sales assistant\nStore: Royal Chaussures\n\n[2. RULES]\n- Reply in Algerian Arabic\n- Use emojis\n- Never say you are AI\n\n[3. PRODUCTS]\n- Sizes: 36-41 EU\n- Delivery: ZR Express all Algeria\n- Payment: Cash on delivery"
                with engine.connect() as _conn:
                    _existing = _conn.execute(_txt("SELECT id FROM ai_settings WHERE store_id = '1'")).fetchone()
                    if _existing:
                        _conn.execute(_txt("UPDATE ai_settings SET ai_model = 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', system_prompt = :p, language = 'ar', temperature = 0.7, max_tokens = 2048, greeting_enabled = TRUE, updated_at = :now WHERE store_id = '1'"), {"p": _ai_prompt, "now": _dt.utcnow()})
                        _seed_result = "updated"
                    else:
                        _conn.execute(_txt("INSERT INTO ai_settings (id, store_id, ai_model, system_prompt, language, temperature, max_tokens, greeting_enabled) VALUES (:id, '1', 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', :p, 'ar', 0.7, 2048, TRUE)"), {"id": str(uuid.uuid4()), "p": _ai_prompt})
                        _seed_result = "created"
                    _conn.commit()
            except Exception as _se:
                _seed_result = f"error: {_se}"

            engine.dispose()
            return jsonify({"status": "ok", "tables": tables, "ai_seed": _seed_result, "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ────────────────────────────────────────────────────────────────
    # Agents Prompts API
    # ────────────────────────────────────────────────────────────────

    AGENTS_DEFINITIONS = [
        {"type": "customer_support", "name": "Customer Support", "icon": "fa-solid fa-headset", "color": "bg-blue-500/10", "text_color": "text-blue-400", "description": "Customer service and inquiries"},
        {"type": "shipping", "name": "Shipping Tracking", "icon": "fa-solid fa-truck-fast", "color": "bg-teal-500/10", "text_color": "text-teal-400", "description": "ZR Express delivery tracking"},
        {"type": "sales", "name": "Sales Agent", "icon": "fa-solid fa-cart-shopping", "color": "bg-neon-purple/10", "text_color": "text-neon-purple", "description": "Product recommendations and sales"},
        {"type": "campaign", "name": "Campaign Agent", "icon": "fa-solid fa-bullhorn", "color": "bg-neon-pink/10", "text_color": "text-neon-pink", "description": "Promotions and seasonal offers"},
        {"type": "engagement", "name": "Engagement Agent", "icon": "fa-solid fa-heart", "color": "bg-emerald-500/10", "text_color": "text-emerald-400", "description": "Customer loyalty and follow-ups"},
        {"type": "analytics", "name": "Analytics Agent", "icon": "fa-solid fa-chart-line", "color": "bg-amber-400/10", "text_color": "text-amber-400", "description": "Reports and KPIs"},
        {"type": "inventory", "name": "Inventory Agent", "icon": "fa-solid fa-warehouse", "color": "bg-amber-400/10", "text_color": "text-amber-400", "description": "Stock and inventory management"},
    ]

    AGENT_DEFAULT_PROMPTS = {
        "customer_support": "You are a helpful customer support agent for Royal Chaussures, a women's shoe and accessories store. You help customers with inquiries, returns, complaints, and general questions. Be polite, professional, and solution-oriented. Reply in Algerian Arabic (Darja) or simple Arabic. Use emojis.",
        "shipping": "You are a shipping tracking agent for Royal Chaussures. You help customers track their orders via ZR Express, check delivery status, and provide estimated delivery times. You cover all 58 wilayas of Algeria. Reply in Algerian Arabic (Darja) or simple Arabic. Use emojis.",
        "sales": "You are a passionate sales agent for Royal Chaussures, a women's shoe and accessories store. Your goal is to help customers find the perfect products, suggest complementary items, and close sales. Know the product catalog well. Sizes available: 36-41 EU. Reply in Algerian Arabic (Darja) or simple Arabic. Use emojis.",
        "campaign": "You are a campaign specialist for Royal Chaussures. You create excitement around promotions, seasonal sales, flash deals, and new arrivals. You encourage customers to take advantage of limited-time offers. Reply in Algerian Arabic (Darja) or simple Arabic. Use emojis.",
        "engagement": "You are a customer engagement agent for Royal Chaussures. You focus on building customer loyalty, sending follow-ups after purchases, requesting reviews, and making customers feel valued. You help with the loyalty program. Reply in Algerian Arabic (Darja) or simple Arabic. Use emojis.",
        "analytics": "You are an analytics agent that provides business insights, reports, and KPIs for Royal Chaussures. You analyze sales data, customer behavior, and channel performance. Present data clearly with numbers and percentages. Reply in Algerian Arabic (Darja) or simple Arabic.",
        "inventory": "You are an inventory management agent for Royal Chaussures. You track stock levels, low-stock alerts, and product availability across all variants and sizes. Help staff manage inventory efficiently. Reply in Algerian Arabic (Darja) or simple Arabic.",
    }

    @app.route("/api/agents/prompts", methods=["GET"])
    def api_agents_prompts_list():
        """Get all agents with their prompts for a store"""
        store_id = request.args.get("store_id", "1")
        try:
            from .database.models import StorePrompt
            from .database.models import get_global_session
            db = get_global_session()
            result = []
            for agent_def in AGENTS_DEFINITIONS:
                agent_type = agent_def["type"]
                stored = db.query(StorePrompt).filter(
                    StorePrompt.store_id == store_id,
                    StorePrompt.agent_type == agent_type
                ).first()
                prompt_text = stored.prompt_text if stored else AGENT_DEFAULT_PROMPTS.get(agent_type, "")
                is_default = stored.is_default if stored else True
                result.append({
                    **agent_def,
                    "prompt": prompt_text,
                    "is_default": is_default,
                })
            db.close()
            return jsonify({"success": True, "agents": result})
        except Exception as e:
            logger.error(f"[AGENTS] List error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/agents/prompts", methods=["POST"])
    def api_agents_prompts_save():
        """Save prompt for a specific agent type"""
        try:
            data = request.get_json(force=True)
            store_id = data.get("store_id", "1")
            agent_type = data.get("agent_type", "")
            prompt_text = data.get("prompt", "")

            if not agent_type:
                return jsonify({"success": False, "error": "agent_type is required"}), 400

            from .database.models import StorePrompt, get_global_session
            db = get_global_session()
            existing = db.query(StorePrompt).filter(
                StorePrompt.store_id == store_id,
                StorePrompt.agent_type == agent_type
            ).first()

            if existing:
                existing.prompt_text = prompt_text
                existing.is_default = False
                existing.updated_at = datetime.now(timezone.utc)
            else:
                sp = StorePrompt(
                    store_id=store_id,
                    agent_type=agent_type,
                    prompt_text=prompt_text,
                    is_default=False
                )
                db.add(sp)

            db.commit()
            db.close()

            logger.info(f"[AGENTS] Saved prompt for {agent_type} (store={store_id})")
            return jsonify({"success": True, "agent_type": agent_type, "saved": True})
        except Exception as e:
            logger.error(f"[AGENTS] Save error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/agents/prompts/<agent_type>", methods=["GET"])
    def api_agents_prompts_get(agent_type):
        """Get prompt for a specific agent type"""
        store_id = request.args.get("store_id", "1")
        try:
            from .database.models import StorePrompt, get_global_session
            db = get_global_session()
            stored = db.query(StorePrompt).filter(
                StorePrompt.store_id == store_id,
                StorePrompt.agent_type == agent_type
            ).first()
            prompt_text = stored.prompt_text if stored else AGENT_DEFAULT_PROMPTS.get(agent_type, "")
            is_default = stored.is_default if stored else True
            db.close()
            return jsonify({
                "success": True,
                "agent_type": agent_type,
                "prompt": prompt_text,
                "is_default": is_default,
                "default_prompt": AGENT_DEFAULT_PROMPTS.get(agent_type, "")
            })
        except Exception as e:
            logger.error(f"[AGENTS] Get error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ────────────────────────────────────────────────────────────────
    # Messages / Conversations API (Live Chat)
    # ────────────────────────────────────────────────────────────────

    @app.route("/api/messages", methods=["GET"])
    def api_messages():
        """Get all messages grouped by conversation (sender_id + platform)"""
        store_id = request.args.get("store_id", "1")
        limit = int(request.args.get("limit", 200))
        platform = request.args.get("platform", "")
        search = request.args.get("search", "")

        try:
            from .database.models import Message, Conversation, get_global_session
            from sqlalchemy import func as _func

            db = get_global_session()
            # Get all conversations for this store
            base = db.query(Conversation).filter(Conversation.store_id == store_id)
            if platform:
                base = base.filter(Conversation.channel == platform)
            logger.info(f"[MESSAGES] Query: store_id={store_id} platform={platform} limit={limit}")
            conversations = base.order_by(Conversation.updated_at.desc()).limit(limit).all()
            logger.info(f"[MESSAGES] Found {len(conversations)} conversations")

            result = []
            for conv in conversations:
                # Get last message for preview
                last_msg = db.query(Message).filter(
                    Message.conversation_id == conv.id
                ).order_by(Message.created_at.desc()).first()

                result.append({
                    "id": conv.id,
                    "store_id": conv.store_id,
                    "channel": conv.channel,
                    "platform_conversation_id": conv.platform_conversation_id,
                    "customer_name": conv.customer_name or "",
                    "customer_platform_id": conv.customer_platform_id or "",
                    "last_user_message": conv.last_user_message or "",
                    "last_ai_reply": conv.last_ai_reply or "",
                    "message_count": conv.message_count or 0,
                    "created_at": conv.created_at.isoformat() if conv.created_at else "",
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else "",
                    "sender_name": conv.customer_name or conv.customer_platform_id or "",
                })

            db.close()

            # Filter by search
            if search:
                q = search.lower()
                result = [r for r in result if q in r["customer_name"].lower() or q in r["customer_platform_id"].lower() or q in r["last_user_message"].lower()]

            return jsonify({"success": True, "conversations": result, "total": len(result)})
        except Exception as e:
            logger.error(f"[MESSAGES] List error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ⚠️ Note: /api/conversations/ routes may be intercepted by conversations_bp Blueprint
    # Using /api/messages/conv prefix instead to avoid Blueprint auth interception

    @app.route("/api/messages/conv/<store_id>/<conv_id>", methods=["GET"])
    def api_conversation_messages(store_id, conv_id):
        """Get all messages for a specific conversation"""
        try:
            from .database.models import Message, Conversation, get_global_session
            db = get_global_session()
            logger.info(f"[MESSAGES] Fetching: store={store_id} conv={conv_id}")

            # Strategy 1: Try by conversation_id (UUID from our system)
            messages = db.query(Message).filter(
                Message.conversation_id == conv_id
            ).order_by(Message.created_at.asc()).limit(100).all()

            # Strategy 2: If no messages found, try by platform_conversation_id (PSID from Meta)
            if not messages:
                logger.info(f"[MESSAGES] No messages by conversation_id, trying platform ID...")
                # First, find the conversation to get both IDs
                conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
                if conv:
                    logger.info(f"[MESSAGES] Found conv: id={conv.id} platform_id={conv.platform_conversation_id} customer_id={conv.customer_platform_id}")
                    # Try platform_conversation_id
                    messages = db.query(Message).filter(
                        Message.conversation_id == conv.id
                    ).order_by(Message.created_at.asc()).limit(100).all()
                    if not messages:
                        # Try customer_platform_id (the PSID / sender ID)
                        messages = db.query(Message).filter(
                            Message.conversation_id == conv.platform_conversation_id
                        ).order_by(Message.created_at.asc()).limit(100).all()
                        if not messages:
                            # Try by matching channel + customer_platform_id
                            messages = db.query(Message).filter(
                                Message.channel == conv.channel,
                                Message.conversation_id == conv.customer_platform_id
                            ).order_by(Message.created_at.asc()).limit(100).all()
                else:
                    # Direct fallback: try conv_id as platform_conversation_id
                    messages = db.query(Message).filter(
                        Message.conversation_id == conv_id
                    ).order_by(Message.created_at.asc()).limit(100).all()

            logger.info(f"[MESSAGES] Found {len(messages)} messages for conv={conv_id}")

            result = []
            for m in messages:
                result.append({
                    "id": m.id,
                    "conversation_id": m.conversation_id,
                    "role": m.role,
                    "content": m.content,
                    "content_type": m.content_type,
                    "image_url": m.image_url or "",
                    "channel": m.channel,
                    "sender_name": m.channel,  # channel as sender identifier
                    "created_at": m.created_at.isoformat() if m.created_at else "",
                })
            db.close()
            return jsonify({"success": True, "messages": result})
        except Exception as e:
            logger.error(f"[MESSAGES] Conversation messages error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/conversations/<store_id>/<conv_id>/messages/raw", methods=["GET"])
    def api_conversation_messages_raw(store_id, conv_id):
        """Debug: Return raw conversation and messages info"""
        try:
            from .database.models import Conversation, Message, get_global_session
            db = get_global_session()
            conv = db.query(Conversation).filter(
                Conversation.id == conv_id,
                Conversation.store_id == store_id
            ).first()
            msgs = db.query(Message).filter(
                Message.conversation_id == conv_id
            ).order_by(Message.created_at.asc()).limit(100).all()
            db.close()
            return jsonify({
                "success": True,
                "conv_exists": conv is not None,
                "conv": {
                    "id": conv.id if conv else None,
                    "store_id": conv.store_id if conv else None,
                    "channel": conv.channel if conv else None,
                    "message_count": conv.message_count if conv else 0,
                    "customer_name": conv.customer_name if conv else None,
                    "customer_platform_id": conv.customer_platform_id if conv else None,
                } if conv else None,
                "messages_count": len(msgs),
                "first_message": {
                    "id": msgs[0].id,
                    "role": msgs[0].role,
                    "content": msgs[0].content[:100] if msgs[0].content else "",
                } if msgs else None,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/profile", methods=["GET"])
    def api_profile():
        """Get Facebook user profile by PSID"""
        psid = request.args.get("psid", "")
        if not psid:
            return jsonify({"success": False, "error": "psid required"}), 400
        try:
            import requests as _req2
            token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
            if not token or not psid:
                return jsonify({"success": False, "name": psid, "fallback": True})
            resp = _req2.get(
                f"https://graph.facebook.com/v21.0/{psid}",
                params={"fields": "name,profile_pic", "access_token": token},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return jsonify({"success": True, "name": data.get("name", psid), "profile_pic": data.get("profile_pic", "")})
            return jsonify({"success": False, "name": psid, "fallback": True})
        except Exception as e:
            logger.error(f"[PROFILE] Error fetching {psid}: {e}")
            return jsonify({"success": False, "name": psid, "fallback": True})

    return app


# ─── Entry Point ──────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", Config.DASHBOARD_PORT))
    logger.info(f"RC Agents SaaS Core starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
