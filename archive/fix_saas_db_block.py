import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('server.py', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# Find the broken block
marker = 'system_prompt = "'
idx = text.find(marker)
if idx < 0:
    print("ERROR: block not found")
    sys.exit(1)

line_start = text.rfind('\n', 0, idx) + 1
next_block = text.find('\n    if not system_prompt:', idx)
if next_block < 0:
    print("ERROR: next block not found")
    sys.exit(1)

old_block = text[line_start:next_block]

# Simple replacement: just skip the sqlalchemy DB read entirely, use env only
new_block = """    # Multi-Tenant: read system prompt from PostgreSQL via subprocess psql
    _model = AI_MODEL  # ALWAYS from env (forced in code)
    system_prompt = ""
    try:
        import subprocess as _sp
        _db_url = os.getenv("SAAS_DATABASE_URL") or os.getenv("DATABASE_URL") or ""
        if _db_url and _db_url.startswith("postgres"):
            _parts = _db_url.split("://")[1].split("@")
            _up = _parts[0].split(":")
            _hd = _parts[1].split("/")
            _hp = _hd[0].split(":")
            _env = os.environ.copy()
            _env["PGPASSWORD"] = _up[1] if len(_up) > 1 else ""
            _dbn = _hd[1].split("?")[0] if len(_hd) > 1 else "rcagents"
            _c = f'psql -h {_hp[0]} -p {int(_hp[1]) if len(_hp) > 1 else 5432} -U {_up[0]} -d {_dbn} -t -A -c "SELECT system_prompt FROM ai_settings WHERE store_id = \\'{store_id}\\'"'
            _r = _sp.run(_c, shell=True, capture_output=True, text=True, timeout=10, env=_env)
            if _r.returncode == 0 and _r.stdout.strip():
                system_prompt = _r.stdout.strip()
                logger.info(f"[AI] Loaded system prompt from DB for store {store_id} ({len(system_prompt)} chars)")
    except Exception as _e:
        logger.warning(f"[AI] DB read skipped (non-critical), using env: {_safe_str(_e)}")
"""

text = text[:line_start] + new_block + text[next_block:]
with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"OK replaced {len(old_block)} chars -> {len(new_block)} chars")
