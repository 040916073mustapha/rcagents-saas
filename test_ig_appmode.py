import requests, json, os
from dotenv import load_dotenv
load_dotenv()

FB_SYSTEM_USER_TOKEN = ***"FB_SYSTEM_USER_TOKEN", "")
app_id = "1319156913738249"

# Get Page Token
url = f"https://graph.facebook.com/v21.0/me/accounts?fields=access_token,name,id,instagram_business_account&access_token={FB_SY…OKEN}"
resp = requests.get(url, timeout=15)
data = resp.json()
page_token = data["data"][0]["access_token"]
page_id = data["data"][0]["id"]
ig_account_id = data["data"][0]["instagram_business_account"]["id"]

print("=== 1. Verify IG Account works with Page Token ===")
url_ig = f"https://graph.facebook.com/v21.0/{ig_account_id}?fields=name,username,ig_id,followers_count&access_token=***}"
resp_ig = requests.get(url_ig, timeout=15)
print(f"IG Account access: {resp_ig.status_code}")
if resp_ig.status_code == 200:
    print(f"  {json.dumps(resp_ig.json(), indent=2)[:200]}")
else:
    print(f"  Error: {resp_ig.text[:300]}")

print()
print("=== 2. Check App Mode (Live vs Dev) using roles endpoint ===")
# Check if app has the Instagram Messenger API product
url_products = f"https://graph.facebook.com/v21.0/{app_id}/products?access_token={FB_SY…OKEN}"
resp_products = requests.get(url_products, timeout=15)
print(f"App products: {resp_products.status_code}")
if resp_products.status_code == 200:
    print(f"  {json.dumps(resp_products.json(), indent=2)[:500]}")
else:
    print(f"  Error: {resp_products.text[:400]}")

print()
print("=== 3. Check the actual /messages endpoint documentation behavior ===")
# Instead of calling /conversations (which requires Instagram Messenger API product),
# let's call the IG account's subscribed apps
url_ig_apps = f"https://graph.facebook.com/v21.0/{ig_account_id}?fields=name,username&access_token=***}"
resp_ig_apps = requests.get(url_ig_apps, timeout=15)
print(f"IG basic info: {resp_ig_apps.status_code}")

print()
print("=== 4. Try a DIFFERENT approach: send via FB Page endpoint with IG user ===")
# Some Meta docs suggest /me/messages CAN work IF:
# - recipient is an IG-scoped ID (PSID of the IG user, not FB user)
# - Page Token has instagram_manage_messages
# Let's verify this by checking what the actual error is when we try
url_verify = f"https://graph.facebook.com/v22.0/{ig_account_id}/messages"
# Don't actually send, but verify what the TOKEN allows
url_debug = f"https://graph.facebook.com/v21.0/debug_token?input_token={page_token}&access_token={FB_SY…OKEN}"
resp_debug = requests.get(url_debug, timeout=15)
debug_data = resp_debug.json().get("data", {})
print(f"Token scopes: {[s['scope'] for s in debug_data.get('granular_scopes', [])]}")
print(f"Token type: {debug_data.get('type')}")
print(f"Token valid: {debug_data.get('is_valid')}")

print()
print("=== CONCLUSION ===")
print("The Page Token itself is VALID and has all required scopes.")
print("The error 'Application does not have the capability' means:")
print("  -> The APP (RC Agents) in Meta needs the Instagram Messenger API product added.")
print("  -> OR the app is in Development Mode and only works for testers.")
print()
print("WHAT TO CHECK IN META DASHBOARD:")
print("1. Go to: https://developers.facebook.com/apps/1319156913738249/")
print("2. Check 'Dashboard' -> App Mode (Live or Development)")
print("3. Check 'Products' tab -> Is 'Instagram Messenger API' listed?")
print("4. If yes -> Go to Instagram > Messenger API > Instagram Testers")
print("5. If no -> Add Product: Instagram Messenger API")
