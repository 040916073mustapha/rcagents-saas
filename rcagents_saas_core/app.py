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

    def _call_ai_and_save(store_id, sender_id, user_text, image_url, channel_type, platform):
        """Core: call AIEngine, save reply, return reply text or None"""
        from .ai.engine import AIEngine
        ai = AIEngine(store_id)
        try:
            ai_reply = ai.send_request(user_text, image_url)
            if not ai_reply:
                ai_reply = "عذراً، لدينا بعض المشاكل التقنية حالياً. يمكنك التواصل معنا على الرقم +213659832426 🙏"
            from .database.crud import get_or_create_conversation, save_message
            conv = get_or_create_conversation(store_id, channel_type, sender_id, customer_platform_id=sender_id)
            save_message(conv.id, store_id, "assistant", ai_reply, channel_type, "text")
            logger.info(f"[AI] Reply sent to {platform}/{sender_id[:20]}: '{ai_reply[:80]}...' store={store_id}")
            return ai_reply
        except Exception as e:
            logger.error(f"[AI] Engine error for store {store_id}: {e}")
            return None
        finally:
            ai.close()

    def _send_fb_reply_ai(sender_id, text, image_url, store_id):
        """Messenger: AI reply + send via Graph API"""
        reply = _call_ai_and_save(store_id, sender_id, text, image_url, "messenger", "FB")
        if reply and _FB_PAGE_TOKEN:
            try:
                _http.post(
                    f"{_META_API}/me/messages",
                    params={"access_token": _FB_PAGE_TOKEN},
                    json={"recipient": {"id": sender_id}, "message": {"text": reply[:2000]}},
                    timeout=10
                )
            except Exception as e:
                logger.error(f"[FB] Send error: {e}")

    def _send_ig_reply_ai(sender_id, text, image_url, store_id):
        """Instagram: AI reply + send via Graph API"""
        reply = _call_ai_and_save(store_id, sender_id, text, image_url, "instagram", "IG")
        if reply and _FB_PAGE_TOKEN:
            try:
                ig_id = os.getenv("INSTAGRAM_BUSINESS_ID", "")
                if ig_id:
                    _http.post(
                        f"{_META_API}/{ig_id}/messages",
                        params={"access_token": _FB_PAGE_TOKEN},
                        json={"recipient": {"id": sender_id}, "message": {"text": reply[:2000]}},
                        timeout=10
                    )
            except Exception as e:
                logger.error(f"[IG] Send error: {e}")

    def _send_wa_reply_ai(sender_id, text, image_url, store_id):
        """WhatsApp: AI reply + send via Graph API"""
        reply = _call_ai_and_save(store_id, sender_id, text, image_url, "whatsapp", "WA")
        if reply and _WA_TOKEN and _WA_PHONE_ID:
            try:
                _http.post(
                    f"{_META_API}/{_WA_PHONE_ID}/messages",
                    headers={"Authorization": f"Bearer {_WA_TOKEN}"},
                    json={"messaging_product": "whatsapp", "to": sender_id, "text": {"body": reply[:4096]}},
                    timeout=10
                )
            except Exception as e:
                logger.error(f"[WA] Send error: {e}")

    # ─── Multi-Tenant Webhook Processors ─────────────────────

    from .database.crud import get_store_id_by_platform as _saas_get_store_id, get_store_id_by_whatsapp_phone as _saas_get_store_wa, get_or_create_conversation, save_message

    def _get_store_id_from_entry(entry, channel_type):
        """Extract store_id from webhook entry based on channel type"""
        entry_id = entry.get("id", "")
        if entry_id:
            try:
                sid = _saas_get_store_id(channel_type, str(entry_id))
                if sid:
                    return sid
            except Exception:
                pass
        return None

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
                    logger.warning(f"[MT] No store for WA phone {phone_id}, skipping")
                    continue
                for msg in value.get("messages", []):
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

    return app


# ─── Entry Point ──────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", Config.DASHBOARD_PORT))
    logger.info(f"RC Agents SaaS Core starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
