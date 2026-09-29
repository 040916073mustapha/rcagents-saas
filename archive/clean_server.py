import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('server.py', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# Find and remove the duplicate blocks
# Pattern: old sqlalchemy comment followed by _model = AI_MODEL
old1 = '# 🆕 Multi-Tenant: قراءة AI Model و System Prompt من قاعدة بيانات SaaS Core\n    _model = AI_MODEL  # default from env\n'
old2 = '    # Multi-Tenant: read AI model + system prompt from PostgreSQL SaaS DB\n    _model = AI_MODEL  # ALWAYS from env (forced in code)\n'

# Remove them in order
if old1 in text:
    text = text.replace(old1, '')
    print('Removed old block 1')

if old2 in text:
    text = text.replace(old2, '')
    print('Removed old block 2')

# Also remove the old except that's orphaned
old_except = "    except Exception as _e:\n        logger.warning(f\"[AI] SaaS DB model read failed, using env default: {_safe_str(_e)}\")\n    \n"
# Check if this except is still there (orphaned)
# It should be after the "SaaS Core" comment and before the new block
# Find it after the old comment removal
lines = text.split('\n')
cleaned = []
skip_next = False
for i, line in enumerate(lines):
    if 'SaaS DB model read failed, using env default' in line:
        skip_next = True
        continue
    if skip_next:
        skip_next = False
        if line.strip() == '':
            continue
    cleaned.append(line)

text = '\n'.join(cleaned)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print(f'Final: {len(text)} chars')
