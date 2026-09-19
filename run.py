"""
RC Agents — Unified Server Entry Point
========================================
Merges SaaS Core (app.py with Supabase) + Legacy Webhooks (server.py)
into a single Flask app for Render deployment.
"""
import os
import sys
import logging

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rc-agents")

# ─── IMPORT SaaS Core (Supabase / PostgreSQL) ─────────────────
from rcagents_saas_core.app import create_app as create_saas_app
saas_app = create_saas_app()
logger.info("✅ SaaS Core app created (Supabase/PostgreSQL)")

# ─── IMPORT Legacy Webhooks (server.py) ───────────────────────
# server.py registers its routes directly on the module-level `app`
import server as legacy_server
logger.info("✅ Legacy webhooks loaded (server.py)")

# ─── MERGE: Copy all legacy routes onto the SaaS app ──────────
for rule in legacy_server.app.url_map.iter_rules():
    endpoint = rule.endpoint
    if endpoint.startswith("static") or endpoint == "pos_direct":
        continue  # skip static and POS fallback (handled by SaaS)
    view_func = legacy_server.app.view_functions.get(endpoint)
    if view_func:
        try:
            saas_app.add_url_rule(
                rule.rule,
                endpoint=f"legacy_{endpoint}",
                view_func=view_func,
                methods=list(rule.methods - {"HEAD", "OPTIONS"}),
            )
        except Exception as e:
            logger.warning(f"Route merge skip {rule.rule}: {e}")

logger.info("✅ Legacy routes merged into SaaS app")

# ─── EXPORT for gunicorn ──────────────────────────────────────
app = saas_app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info(f"🚀 RC Agents starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
