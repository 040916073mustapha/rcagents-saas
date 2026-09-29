#!/usr/bin/env python3
"""Fix the except block directly by line manipulation"""

with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the except block
target_line = None
for i, line in enumerate(lines):
    if 'except requests.exceptions.Timeout:' in line and i > 800:
        target_line = i
        break

if target_line:
    print(f"Found Timeout except at line {target_line+1}")
    # The replacement block
    new_lines = [
        "    except requests.exceptions.Timeout:\n",
        '        logger.error(f"[AI] timeout after 180s \xe2\x80\x94 model={_model}, retrying fallback...")\n',
        "        # Retry with a lighter fallback model\n",
        "        try:\n",
        '            fb_model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"\n',
        "            if _model != fb_model and user_message:\n",
        '                logger.info(f"[AI] Fallback to {fb_model}")\n',
        "                fallback_payload = payload.copy()\n",
        '                fallback_payload["model"] = fb_model\n',
        '                fallback_payload["max_tokens"] = 200\n',
        "                fb_resp = requests.post(AI_API_URL, json=fallback_payload, headers=headers, timeout=120)\n",
        "                if fb_resp.status_code == 200:\n",
        '                    reply = fb_resp.json()["choices"][0]["message"]["content"].strip()\n',
        "                    if reply:\n",
        '                        add_to_conversation(sender_id, "user", user_message, store_id)\n',
        '                        add_to_conversation(sender_id, "assistant", reply, store_id)\n',
        '                        logger.info(f"[AI] Fallback reply sent ({len(reply)} chars)")\n',
        "                        return reply\n",
        "        except Exception as fb_e:\n",
        '            logger.warning(f"[AI] Fallback failed: {_safe_str(fb_e)}")\n',
        "    except requests.exceptions.ConnectionError as ce:\n",
        '        logger.error(f"[AI] CONNECTION ERROR: {ce}")\n',
        "    except Exception as e:\n",
        '        logger.error("AI reply error: " + _safe_str(e))\n',
        '    return "Merci de nous contacter! Nous reviendrons vers vous bientot."\n',
    ]
    
    # Replace lines: target_line to target_line + 4 (except + 3 lines + return)
    old_len = 7  # lines 809 to 815 inclusive
    lines[target_line:target_line+old_len] = new_lines
    
    with open('server.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Replaced {old_len} lines with {len(new_lines)} lines")
    print("Done!")
else:
    print("Could not find the except block")
