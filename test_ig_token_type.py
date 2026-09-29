import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

ig_token = os.getenv("FB_SYSTEM_USER_TOKEN", "")
ig_account_id = "17841473888839712"

print(f"Token prefix: {ig_token[:20]}...")
print(f"Token starts with IGAA: {ig_token.startswith('IGAA')}")
print()

# Test 1: Can we access IG account with this token?
print("=== TEST 1: IG account info ===")
params = {"fields": "name,username", "access_token": ig_token}
resp = requests.get("https://graph.facebook.com/v21.0/" + ig_account_id, params=params, timeout=15)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"  {json.dumps(resp.json(), indent=2)}")
else:
    print(f"  Error: {resp.text[:400]}")

# Test 2: Check token debug
print()
print("=== TEST 2: Token Debug ===")
debug_url = "https://graph.facebook.com/v21.0/debug_token"
debug_params = {"input_token": ig_token, "access_token": ig_token}
resp_d = requests.get(debug_url, params=debug_params, timeout=15)
print(f"Status: {resp_d.status_code}")
if resp_d.status_code == 200:
    d = resp_d.json().get("data", {})
    print(f"  Type: {d.get('type')}")
    print(f"  Valid: {d.get('is_valid')}")
    print(f"  App: {d.get('application')}")
    print(f"  Expires: {d.get('expires_at')}")
    scopes = [s['scope'] for s in d.get('granular_scopes', [])]
    print(f"  Granular scopes: {scopes}")
else:
    print(f"  Error: {resp_d.text[:400]}")

# Test 3: Can we see conversations?
print()
print("=== TEST 3: Conversations ===")
conv_params = {"fields": "id,participants", "access_token": ig_token}
resp_conv = requests.get("https://graph.facebook.com/v25.0/" + ig_account_id + "/conversations", params=conv_params, timeout=15)
print(f"Status: {resp_conv.status_code}")
if resp_conv.status_code == 200:
    convs = resp_conv.json().get("data", [])
    print(f"  Conversations: {len(convs)}")
    for c in convs:
        print(f"  - ID: {c.get('id')}")
        parts = c.get("participants", {}).get("data", [])
        print(f"    Participants: {[p.get('id','') for p in parts]}")
else:
    print(f"  Error: {resp_conv.text[:400]}")

# Test 4: Can we get the page info?
print()
print("=== TEST 4: /me/accounts (to get Page Token) ===")
me_params = {"fields": "instagram_business_account,access_token,name,id", "access_token": ig_token}
resp_me = requests.get("https://graph.facebook.com/v21.0/me/accounts", params=me_params, timeout=15)
print(f"Status: {resp_me.status_code}")
if resp_me.status_code == 200:
    for page in resp_me.json().get("data", []):
        print(f"  Page: {page.get('name')} (ID: {page.get('id')})")
        ig = page.get("instagram_business_account", {})
        print(f"  IG: {ig.get('id') if ig else 'NONE'}")
else:
    print(f"  Error: {resp_me.text[:400]}")
