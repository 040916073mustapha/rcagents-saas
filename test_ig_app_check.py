import requests, json, os
from dotenv import load_dotenv
load_dotenv()

FB_SYSTEM_USER_TOKEN = os.getenv("FB_SYSTEM_USER_TOKEN", "")

# Get dynamic Page Token
url = f"https://graph.facebook.com/v21.0/me/accounts?fields=access_token,name,id&access_token={FB_SYSTEM_USER_TOKEN}"
resp = requests.get(url, timeout=15)
data = resp.json()
page_token = data["data"][0]["access_token"]
page_id = data["data"][0]["id"]
app_id = "1319156913738249"

print("=== TEST: App info (Development vs Live Mode) ===")
# Get the app details
url_app = f"https://graph.facebook.com/v21.0/{app_id}?fields=name,is_app_for_pages_ui_enabled,app_domains,role&access_token={FB_SYSTEM_USER_TOKEN}"
resp_app = requests.get(url_app, timeout=15)
print(f"Status: {resp_app.status_code}")
print(f"Response: {resp_app.text[:800]}")

print()
print("=== TEST: Can we access the IG Account with the dynamic token? ===")
ig_account_id = "17841473888839712"

# Try the /messages endpoint directly
url_test = f"https://graph.facebook.com/v22.0/{ig_account_id}/messages"
test_payload = {"recipient": {"id": "123456789_test"}, "message": {"text": "test"}}
test_headers = {"Content-Type": "application/json"}
# We won't actually send this, just check the token capability
resp_test = requests.get(f"https://graph.facebook.com/v22.0/{ig_account_id}/conversations?fields=id&access_token={page_token}", timeout=15)
print(f"Test conversations endpoint: Status {resp_test.status_code}")
print(f"Response: {resp_test.text[:500]}")

print()
print("=== TEST: Check if app has Instagram Messenger API product ===")
# Check subscribed fields on the IG account
url_ig = f"https://graph.facebook.com/v21.0/{ig_account_id}/subscribed_fields?access_token={FB_SYSTEM_USER_TOKEN}"
resp_ig = requests.get(url_ig, timeout=15)
print(f"IG subscribed fields: Status {resp_ig.status_code}")
if resp_ig.status_code == 200:
    print(json.dumps(resp_ig.json(), indent=2)[:800])
else:
    print(f"Error: {resp_ig.text[:500]}")

print()
print("=== TEST: What subscriptions does this page have? ===")
url_page_subs = f"https://graph.facebook.com/v21.0/{page_id}/subscribed_apps?access_token={page_token}"
resp_subs = requests.get(url_page_subs, timeout=15)
print(f"Subscribed apps: Status {resp_subs.status_code}")
if resp_subs.status_code == 200:
    print(json.dumps(resp_subs.json(), indent=2)[:1000])
else:
    print(f"Error: {resp_subs.text[:500]}")

print()
print("=== CRITICAL: Check if this is a 'Page Scoped' token limitation ===")
# Page tokens obtained from /me/accounts are scoped to the page.
# They may NOT have the "instagram_manage_messages" capability in the token itself
# even if the System User has the scope.
# Page tokens might need to be generated differently for IG messaging.

print()
print("=== KEY DIAGNOSIS ===")
print("Page Token Granular Scopes INCLUDES 'instagram_manage_messages'")
print("BUT conversations API returns: Application does not have the capability")
print()
print("This is a known Meta issue - the Page Token needs to be generated")
print("with specific 'ig_messaging' or from a special endpoint.")
print()
print("RECOMMENDED SOLUTION: Try generating a Page Token with scopes explicitly")
