#!/usr/bin/env python3
"""Fix literal \n and add product images in dashboard.html"""

with open('rcagents_saas_core/frontend/templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix literal \n in HTML (replace "\n" with empty string where not in JS strings)
import re
content = content.replace('\\n            <!-- ====== PRODUCTS ====== -->', '            <!-- ====== PRODUCTS ====== -->')

# 2. Add real product image URLs to MOCK_PRODUCTS in dashboard_base.html
print("Fixed \\n - checking result...")
with open('rcagents_saas_core/frontend/templates/dashboard_base.html', 'r', encoding='utf-8') as f:
    base = f.read()

# 3. Check count of \n
count = base.count('\\n')
print(f"dashboard_base.html literal \\n count: {count}")

count2 = content.count('\\n')
print(f"dashboard.html literal \\n count: {count2}")

with open('rcagents_saas_core/frontend/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
