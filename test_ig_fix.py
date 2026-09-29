import requests, json, os
from dotenv import load_dotenv
load_dotenv()

FB_SYSTEM_USER_TOKEN = os.getenv("FB_SYSTEM_USER_TOKEN", "")

# Get Page Token and IDs
url = f"https://graph.facebook.com/v21.0/me/accounts?fields=access_token,name,id&access_token={FB_SYSTEM_USER_TOKEN}"
resp = requests.get(url, timeout=15)
data = resp.json()
page_token = data["data"][0]["access_token"]
page_id = data["data"][0]["id"]
app_id = "1319156913738249"

print("=== STEP 1: Subscribe app to 'instagram_manage_messages' on the Page ===")
url_sub = f"https://graph.facebook.com/v21.0/{page_id}/subscribed_apps?subscribed_fields=messages,messaging_postbacks,instagram_manage_messages&access_token={page_token}"
resp_sub = requests.post(url_sub, timeout=15)
print(f"Status: {resp_sub.status_code}")
if resp_sub.status_code == 200:
    print(f"✅ Success! Response: {json.dumps(resp_sub.json(), indent=2)}")
else:
    print(f"❌ Failed: {resp_sub.text[:500]}")
    # Try with System User Token
    print()
    print("Trying with System User Token instead...")
    url_sub2 = f"https://graph.facebook.com/v21.0/{page_id}/subscribed_apps?subscribed_fields=messages,messaging_postbacks,instagram_manage_messages&access_token={FB_SYSTEM_USER_TOKEN}"
    resp_sub2 = requests.post(url_sub2, timeout=15)
    print(f"Status: {resp_sub2.status_code}")
    if resp_sub2.status_code == 200:
        print(f"✅ Success! Response: {json.dumps(resp_sub2.json(), indent=2)}")
    else:
        print(f"❌ Failed: {resp_sub2.text[:500]}")

# Check result
print()
print("=== Verify subscribed fields after update ===")
url_check = f"https://graph.facebook.com/v21.0/{page_id}/subscribed_apps?access_token={page_token}"
resp_check = requests.get(url_check, timeout=15)
print(f"Status: {resp_check.status_code}")
if resp_check.status_code == 200:
    for app in resp_check.json().get("data", []):
        print(f"  App: {app.get('name')}")
        print(f"  Subscribed fields: {app.get('subscribed_fields')}")
        break
else:
    print(f"Error: {resp_check.text[:500]}")
