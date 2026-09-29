import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

FB_SYSTEM_USER_TOKEN = ***"FB_SYSTEM_USER_TOKEN", "")
# Workaround: clean any hidden chars
FB_SYSTEM_USER_TOKEN = FB_SYSTEM_USER_TOKEN.strip()
ig_account_id = "17841473888839712"
page_id = "1040729219115342"

print("=== TEST 1: System User Token - Get Page + IG Account ===")
params = {
    "fields": "instagram_business_account,access_token,name,id",
    "access_token": FB_SYSTEM_USER_TOKEN
}
resp = requests.get("https://graph.facebook.com/v21.0/me/accounts", params=params, timeout=15)
print(f"Status: {resp.status_code}")
page_token = ""
if resp.status_code == 200:
    data = resp.json()
    for page in data.get("data", []):
        page_token = page.get("access_token", "")
        print(f"  Page: {page.get('name')} (ID: {page.get('id')})")
        ig = page.get("instagram_business_account", {})
        print(f"  IG Account: {ig.get('id') if ig else 'NONE'}")
        if page_token:
            print(f"  Page Token prefix: {page_token[:15]}...")
            print(f"  Page Token length: {len(page_token)}")
else:
    print(f"  Error: {resp.text[:500]}")

if page_token:
    print()
    print("=== TEST 2: Token Debug ===")
    debug_params = {"input_token": page_token, "access_token": FB_SYSTEM_USER_TOKEN}
    resp_d = requests.get("https://graph.facebook.com/v21.0/debug_token", params=debug_params, timeout=15)
    if resp_d.status_code == 200:
        d = resp_d.json().get("data", {})
        print(f"  Type: {d.get('type')}")
        print(f"  Valid: {d.get('is_valid')}")
        scopes = [s['scope'] for s in d.get('granular_scopes', [])]
        print(f"  Scopes: {scopes}")
        has_ig = 'instagram_manage_messages' in scopes
        print(f"  Has instagram_manage_messages: {has_ig}")
    else:
        print(f"  Error: {resp_d.text[:300]}")

    print()
    print("=== TEST 3: Conversations API (key test!) ===")
    conv_params = {"fields": "id,participants", "access_token": page_token}
    resp_conv = requests.get("https://graph.facebook.com/v25.0/" + ig_account_id + "/conversations", params=conv_params, timeout=15)
    print(f"Status: {resp_conv.status_code}")
    if resp_conv.status_code == 200:
        convs = resp_conv.json().get("data", [])
        print(f"  Conversations count: {len(convs)}")
        for c in convs[:3]:
            print(f"  - ID: {c.get('id')}")
    else:
        print(f"  Error: {resp_conv.text[:400]}")

print()
print("=== VERDICT ===")
if page_token and has_ig:
    conv_ok = 'resp_conv' in dir() and resp_conv.status_code == 200
    if conv_ok:
        print("  ✅ ALL SYSTEMS GO! Token works, IG available, Conversations accessible!")
    else:
        print("  ⚠️ Token works + IG scope present, but Conversations API still blocked")
        print("  → Check if App is in LIVE mode at Meta Dashboard")
elif page_token:
    print("  ⚠️ Page token works but missing instagram_manage_messages scope")
else:
    print("  ❌ Token validation failed")
