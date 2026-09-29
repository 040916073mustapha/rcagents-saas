import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

FB_SYSTEM_USER_TOKEN = os.getenv("FB_SYSTEM_USER_TOKEN", "")
app_id = "1319156913738249"
page_id = "1040729219115342"
ig_account_id = "17841473888839712"

# Get fresh page token
url = "https://graph.facebook.com/v21.0/me/accounts?fields=access_token,name,id&access_token=" + FB_SYSTEM_USER_TOKEN
resp = requests.get(url, timeout=15)
data = resp.json()
page_token = data["data"][0]["access_token"]

print("=== 1. IG Account accessible via Page Token? ===")
url_ig = "https://graph.facebook.com/v21.0/" + ig_account_id + "?fields=name,username&access_token=" + page_token
resp_ig = requests.get(url_ig, timeout=15)
print(f"Status: {resp_ig.status_code}")
if resp_ig.status_code == 200:
    igdata = resp_ig.json()
    print(f"  Name: {igdata.get('name')}")
    print(f"  Username: {igdata.get('username')}")
else:
    print(f"  Error: {resp_ig.text[:300]}")

print()
print("=== 2. Check if Page subscribed apps include Instagram ===")
url_subs = "https://graph.facebook.com/v21.0/" + page_id + "/subscribed_apps?access_token=" + page_token
resp_subs = requests.get(url_subs, timeout=15)
print(f"Status: {resp_subs.status_code}")
if resp_subs.status_code == 200:
    for app in resp_subs.json().get("data", []):
        print(f"  App: {app.get('name')}")
        print(f"  Subscribed fields: {app.get('subscribed_fields')}")
        
print()
print("=== 3. Token debug info ===")
url_debug = "https://graph.facebook.com/v21.0/debug_token?input_token=" + page_token + "&access_token=" + FB_SYSTEM_USER_TOKEN
resp_debug = requests.get(url_debug, timeout=15)
d = resp_debug.json().get("data", {})
print(f"  Type: {d.get('type')}")
print(f"  Valid: {d.get('is_valid')}")
print(f"  Expires: {d.get('expires_at')} (0=never)")
print(f"  Scopes: {[s['scope'] for s in d.get('granular_scopes', [])]}")

print()
print("=== 4. Quick test: can we actually send? (need sender from DB) ===")
# Check if there are any stored IG sender IDs
import sqlite3
conn = sqlite3.connect("royal_orders.db")
c = conn.cursor()
c.execute("SELECT DISTINCT sender_id FROM messages WHERE platform='instagram'")
senders = c.fetchall()
print(f"IG senders in DB: {senders}")
conn.close()

print()
print("=== 5. Check rcagents.db for channel mapping ===")
conn2 = sqlite3.connect("rcagents.db")
c2 = conn2.cursor()
c2.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for r in c2.fetchall():
    if "channels" in r[0].lower() or "stores" in r[0] or "instagram" in r[0].lower():
        print(f"Table: {r[0][:200]}")
        print()
conn2.close()
