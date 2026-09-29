#!/usr/bin/env python3
"""Fix AI timeout: increase to 180s + add fallback model"""

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix timeout from 90 to 180 (first occurrence only)
content = content.replace(
    'resp = requests.post(AI_API_URL, json=payload, headers=headers, timeout=90)',
    'resp = requests.post(AI_API_URL, json=payload, headers=headers, timeout=180)'
)

# 2. Fix the exception handler to add fallback
old_except = (
    "    except requests.exceptions.Timeout:\n"
    '        logger.error(f"[AI] timeout after 90s — model={_model}")'
)

new_except = (
    "    except requests.exceptions.Timeout:\n"
    '        logger.error(f"[AI] timeout after 180s — model={_model}, retrying fallback...")\n'
    "        # Retry with a lighter fallback model\n"
    "        try:\n"
    '            fb_model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"\n'
    "            if _model != fb_model and user_message:\n"
    '                logger.info(f"[AI] Fallback to {fb_model}")\n'
    "                fallback_payload = payload.copy()\n"
    '                fallback_payload["model"] = fb_model\n'
    '                fallback_payload["max_tokens"] = 200\n'
    "                fb_resp = requests.post(AI_API_URL, json=fallback_payload, headers=headers, timeout=120)\n"
    "                if fb_resp.status_code == 200:\n"
    '                    reply = fb_resp.json()["choices"][0]["message"]["content"].strip()\n'
    "                    if reply:\n"
    "                        add_to_conversation(sender_id, \"user\", user_message, store_id)\n"
    "                        add_to_conversation(sender_id, \"assistant\", reply, store_id)\n"
    '                        logger.info(f"[AI] Fallback reply sent ({len(reply)} chars)")\n'
    "                        return reply\n"
    "        except Exception as fb_e:\n"
    '            logger.warning(f"[AI] Fallback failed: {_safe_str(fb_e)}")'
)

if old_except in content:
    content = content.replace(old_except, new_except)
    print("Replaced timeout except block!")
else:
    print("Old except block NOT FOUND - checking exact match...")
    # Find it manually
    idx = content.find("except requests.exceptions.Timeout:")
    if idx >= 0:
        print(f"Found at position {idx}")
        # Show surrounding context
        print(repr(content[idx:idx+100]))

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open('server.py', 'r', encoding='utf-8') as f:
    verify = f.read()
    
if 'timeout=180' in verify:
    print("OK - timeout increased to 180")
if 'Fallback to' in verify:
    print("OK - fallback model added")
if 'timeout after 180s' in verify:
    print("OK - log message updated")
