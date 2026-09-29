import requests, json, os
from dotenv import load_dotenv
load_dotenv()

FB_SYSTEM_USER_TOKEN = os.getenv("FB_SYSTEM_USER_TOKEN", "")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID", "")

print("=== TEST 1: System User -> Page Token + IG Business Account ===")
url = f"https://graph.facebook.com/v21.0/me/accounts?fields=instagram_business_account,access_token,name,id&access_token={FB_SYSTEM_USER_TOKEN}"
resp = requests.get(url, timeout=15)
data = resp.json()
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    for page in data.get("data", []):
        name = page.get("name", "")
        pid = page.get("id", "")
        tok = page.get("access_token", "")
        ig = page.get("instagram_business_account", {})
        print(f"  Page: {name} (ID: {pid})")
        print(f"  Page Token prefix: {tok[:30]}...")
        if ig:
            ig_id = ig.get("id", "")
            print(f"  IG Business Account ID: {ig_id}")
            print(f"  INSTAGRAM_USER_ID in env: {INSTAGRAM_USER_ID}")
            print(f"  Match: {ig_id == INSTAGRAM_USER_ID}")
        else:
            print("  NO Instagram Business Account linked!")
else:
    print(f"Error: {resp.text[:500]}")

print()
print("=== TEST 2: System User Token Scopes ===")
url2 = f"https://graph.facebook.com/v21.0/me/permissions?access_token={FB_SYSTEM_USER_TOKEN}"
resp2 = requests.get(url2, timeout=15)
data2 = resp2.json()
for p in data2.get("data", []):
    perm = p.get("permission", "")
    status = p.get("status", "")
    print(f"  {perm}: {status}")

print()
print("=== TEST 3: Get IG Conversations (test token capability) ===")
# Use the dynamic page token
page_token = data.get("data", [{}])[0].get("access_token", "") if resp.status_code == 200 else ""
ig_account_id = data.get("data", [{}])[0].get("instagram_business_account", {}).get("id", "") if resp.status_code == 200 else ""

if page_token and ig_account_id:
    url3 = f"https://graph.facebook.com/v21.0/me/accounts?access_token={FB_SYSTEM_USER_TOKEN}"
    resp3 = requests.get(url3, timeout=15)
    if resp3.status_code == 200:
        for p in resp3.json().get("data", []):
            if p.get("id") == "1040729219115342":
                page_token = p.get("access_token", "")
                break
    
    # Try to access IG account with page token
    url4 = f"https://graph.facebook.com/v21.0/{ig_account_id}?fields=name,username,ig_id&access_token={page_token}"
    resp4 = requests.get(url4, timeout=15)
    print(f"IG Account Info: Status {resp4.status_code}")
    if resp4.status_code == 200:
        print(f"  {json.dumps(resp4.json(), indent=2)}")
    else:
        print(f"  Error: {resp4.text[:500]}")

print()
print("=== TEST 4: Verify send_ig_reply endpoint and payload ===")
print(f"Endpoint: POST https://graph.facebook.com/v22.0/{ig_account_id}/messages")
print(f"Payload: {{\"recipient\": {{\"id\": \"SENDER_PSID\"}}, \"message\": {{\"text\": \"Test message\"}}}}")
print(f"Token: Dynamic Page Token from System User")
print()
print("=== TEST 5: Check for /me/messages differences ===")
print("Old method: POST /v18.0/me/messages?access_token={PageToken}")
print("  - Routes to Facebook Messenger")
print("New method: POST /v22.0/{ig_account_id}/messages?access_token={PageToken}")
print("  - Routes to Instagram Direct Messages")
print()
print("=== SILENT DROP ANALYSIS ===")
print("If 200 OK but message doesn't appear, possible causes:")
print("1. Token does not have 'instagram_manage_messages' scope")
print("2. Target sender_id is not a valid Instagram PSID")
print("3. Instagram Business Account not properly linked to Page")
print("4. Meta's spam/fraud detection silently drops the message")
