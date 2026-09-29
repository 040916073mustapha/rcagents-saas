#!/usr/bin/env python3
"""Fix the broken sqlalchemy -> subprocess replacement in server.py"""
import re

with open('server.py', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# Find the broken section starting with 'system_prompt = "'
# and ending at the next 'if not system_prompt:'
old = r"system_prompt = \"\"\n    try:\n        import subprocess.*?"
# Find from after the previous except until 'if not system_prompt:'
import re
# Find the broken block
idx = text.find('system_prompt = "')
if idx > 0:
    # Find start of this line
    line_start = text.rfind('\n', 0, idx) + 1
    # Find the next 'if not system_prompt:' block
    next_block = text.find('\n    if not system_prompt:', idx)
    if next_block > 0:
        old_block = text[line_start:next_block]
        new_block = """    # Multi-Tenant: read AI model + system prompt from PostgreSQL SaaS DB
    _model = AI_MODEL  # ALWAYS from env (forced in code)
    system_prompt = ""
    try:
        import subprocess as _sp
        _db_url = os.getenv("SAAS_DATABASE_URL") or os.getenv("DATABASE_URL") or ""
        if _db_url and _db_url.startswith("postgres"):
            _parts = _db_url.split("://")[1].split("@")
            _user_pass = _parts[0].split(":")
            _host_db = _parts[1].split("/")
            _user = _user_pass[0]
            _password = _user_pass[1] if len(_user_pass) > 1 else ""
            _host_port = _host_db[0].split(":")
            _host = _host_port[0]
            _port = int(_host_port[1]) if len(_host_port) > 1 else 5432
            _dbname = _host_db[1].split("?")[0] if len(_host_db) > 1 else "rcagents"
            _env = os.environ.copy()
            _env["PGPASSWORD"] = _password
            _cmd = 'psql -h %s -p %d -U %s -d %s -t -A -c "SELECT system_prompt FROM ai_settings WHERE store_id = \\'%s\\'"' % (_host, _port, _user, _dbname, store_id)
            _r = _sp.run(_cmd, shell=True, capture_output=True, text=True, timeout=10, env=_env)
            if _r.returncode == 0 and _r.stdout.strip():
                system_prompt = _r.stdout.strip()
                logger.info(f"[AI] Loaded system prompt from DB for store {store_id} ({len(system_prompt)} chars)")
                _upd = 'psql -h %s -p %d -U %s -d %s -c "UPDATE ai_settings SET ai_model = \\'%s\\', updated_at = NOW() WHERE store_id = \\'%s\\'"' % (_host, _port, _user, _dbname, "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", store_id)
                _sp.run(_upd, shell=True, capture_output=True, timeout=10, env=_env)
    except Exception as _e:
        logger.warning(f"[AI] DB read skipped (non-critical), using env: {_safe_str(_e)}")
"""
        text = text[:line_start] + new_block + text[next_block:]
        with open('server.py', 'w', encoding='utf-8') as f:
            f.write(text)
        print("✅ Fixed! Replaced broken block (%d chars) with clean version (%d chars)" % (len(old_block), len(new_block)))
    else:
        print("❌ Could not find next 'if not system_prompt:' block")
else:
    print("❌ Could not find 'system_prompt = \"' in file")
