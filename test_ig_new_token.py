import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

FB_SYSTEM_USER_TOKEN = os.getenv("FB_SYSTEM_USER_TOKEN", "")
app_id = "1319156913738249"
page_id = "1040729219115342"
ig_account_id = "17841473888839712"

print("=== TEST 1: Get fresh Page Token from NEW System User Token ===")
url = "https://graph.facebook.com/v21.0/me/accounts"
params = {
    "fields": "instagram_business_account,access_token,name,id",
    "access_token": FB_SYSTEM_USER_TOKEN
}
resp = requests.get(url, params=params, timeout=15)
data = resp.json()
print(f"Status: {resp.status_code}")
ptok = ""
if resp.status_code == 200:
    for page in data.get("data", []):
        ptok = page.get("access_token", "")
        print(f"  Page: {page.get('name')} (ID: {page.get('id')})")
        print(f"  Page Token prefix: {ptok[:30]}...")
        print(f"  Page Token length: {len(ptok)}")
        ig = page.get("instagram_business_account", {})
        print(f"  IG Account: {ig.get('id') if ig else 'NONE'}")

else:
    print(f"  Error: {resp.text[:500]}")

print()
print("=== TEST 2: Token Debug ===")
if ptok:
    debug_url = "https://graph.facebook.com/v21.0/debug_token"
    debug_params = {"input_token": ptok, "access_token": FB_SYSTEM_USER_TOKEN}
    resp_d = requests.get(debug_url, params=debug_params, timeout=15)
    d = resp_d.json().get("data", {})
    print(f"  Type: {d.get('type')}")
    print(f"  Valid: {d.get('is_valid')}")
    scopes = [s['scope'] for s in d.get('granular_scopes', [])]
    print(f"  Scopes: {scopes}")
    print(f"  Has instagram_manage_messages: {'instagram_manage_messages' in scopes}")

print()
print("=== TEST 3: IG Account accessible via Page Token ===")
if ptok:
    ig_url = "https://graph.facebook.com/v21.0/" + ig_account_id
    ig_params = {"fields": "name,username", "access_token": ptok}
    resp_ig = requests.get(ig_url, params=ig_params, timeout=15)
    print(f"Status: {resp_ig.status_code}")
    if resp_ig.status_code == 200:
        igd = resp_ig.json()
        print(f"  Name: {igd.get('name')}")
        print(f"  Username: {igd.get('username')}")
    else:
        print(f"  Error: {resp_ig.text[:300]}")

print()
print("=== TEST 4: Conversations API (should work after dashboard fix) ===")
if ptok:
    conv_url = "https://graph.facebook.com/v25.0/" + ig_account_id + "/conversations"
    conv_params = {"fields": "id,participants", "access_token": ptok}
    resp_conv = requests.get(conv_url, params=conv_params, timeout=15)
    print(f"Status: {resp_conv.status_code}")
    if resp_conv.status_code == 200:
        convs = resp_conv.json().get("data", [])
        print(f"  Conversations count: {len(convs)}")
        for c in convs:
            print(f"  - ID: {c.get('id')}")
            parts = c.get("participants", {}).get("data", [])
            print(f"    Participants: {[p.get('id','') for p in parts]}")
    else:
        print(f"  Error: {resp_conv.text[:400]}")

print()
print("=== SUMMARY ===")
if ptok:
    debug_url2 = "https://graph.facebook.com/v21.0/debug_token"
    debug_params2 = {"input_token": ptok, "access_token": FB_SYSTEM_USER_TOKEN}
    resp_d2 = requests.get(debug_url2, params=debug_params2, timeout=15)
    d2 = resp_d2.json().get("data", {})
    scopes2 = [s['scope'] for s in d2.get('granular_scopes', [])]
    has_ig = 'instagram_manage_messages' in scopes2
    conv_ok = 'resp_conv' in dir() and resp_conv.status_code == 200
    print(f"  Token valid: {d2.get('is_valid')}")
    print(f"  Has instagram_manage_messages scope: {has_ig}")
    if conv_ok:
        print(f"  ✅ Conversations API accessible - READY TO SEND!")
    elif has_ig:
        print(f"  ⚠️ Token has scope but app still needs Instagram Messenger API product")
    else:
        print(f"  ❌ Still blocked")
