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

print("=== Page Token Permission Check ===")
# Check what permissions the PAGE TOKEN has (not the System User token)
url_perms = f"https://graph.facebook.com/v21.0/me/permissions?access_token={page_token}"
resp_perms = requests.get(url_perms, timeout=15)
print(f"Status: {resp_perms.status_code}")
if resp_perms.status_code == 200:
    print("Page Token permissions:")
    for p in resp_perms.json().get("data", []):
        perm = p.get("permission", "")
        status = p.get("status", "")
        print(f"  {perm}: {status}")
else:
    print(f"Error: {resp_perms.text[:500]}")

print()
print("=== Check Page Token Debug Info ===")
url_debug = f"https://graph.facebook.com/v21.0/debug_token?input_token={page_token}&access_token={FB_SYSTEM_USER_TOKEN}"
resp_debug = requests.get(url_debug, timeout=15)
print(f"Status: {resp_debug.status_code}")
if resp_debug.status_code == 200:
    debug_data = resp_debug.json().get("data", {})
    print(f"  App ID: {debug_data.get('app_id')}")
    print(f"  Type: {debug_data.get('type')}")
    print(f"  Application: {debug_data.get('application')}")
    print(f"  Expires at: {debug_data.get('expires_at')}")
    print(f"  Is valid: {debug_data.get('is_valid')}")
    print(f"  Granular scopes: {json.dumps(debug_data.get('granular_scopes', []), indent=4)}")
    print(f"  FBAA scopes: {json.dumps(debug_data.get('fbaa_scopes', []), indent=4)}")
else:
    print(f"Error: {resp_debug.text[:500]}")

print()
print("=== System User Token Debug Info ===")
url_debug_sys = f"https://graph.facebook.com/v21.0/debug_token?input_token={FB_SYSTEM_USER_TOKEN}&access_token={FB_SYSTEM_USER_TOKEN}"
resp_debug_sys = requests.get(url_debug_sys, timeout=15)
print(f"Status: {resp_debug_sys.status_code}")
if resp_debug_sys.status_code == 200:
    debug_sys = resp_debug_sys.json().get("data", {})
    print(f"  App ID: {debug_sys.get('app_id')}")
    print(f"  Type: {debug_sys.get('type')}")
    print(f"  Application: {debug_sys.get('application')}")
    print(f"  Is valid: {debug_sys.get('is_valid')}")
    print(f"  Granular scopes: {json.dumps(debug_sys.get('granular_scopes', []), indent=4)}")
else:
    print(f"Error: {resp_debug_sys.text[:500]}")

print()
print("=== KEY FINDING ===")
print("Application does not have the capability to make this API call")
print("This means the Page Token lacks the Instagram Messaging API capability!")
print()
print("Possible Solutions:")
print("1. The app needs to pass App Review for instagram_manage_messages")
print("2. Add Instagram Messenger API product in Meta Developer Console")
print("3. Check if the app is in Development Mode (only testers can send)")
print("4. Ensure the System User was granted permissions via App listing")
