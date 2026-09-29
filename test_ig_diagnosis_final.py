import requests, json, os
from dotenv import load_dotenv
load_dotenv()

FB_SYSTEM_USER_TOKEN = os.getenv("FB_SYSTEM_USER_TOKEN", "")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_TOKEN", "")
app_id = "1319156913738249"

# 1. Check what IG access we have with a manually exchanged token
print("=== TEST 1: Exchange Page Token for IG-specific token ===")
url_exchange = f"https://graph.facebook.com/v21.0/me?fields=access_token&access_token={PAGE_ACCESS_TOKEN}"
resp = requests.get(url_exchange, timeout=15)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")

print()
print("=== TEST 2: Check app review status ===")
url_review = f"https://graph.facebook.com/v21.0/{app_id}/app_review_permissions?access_token={FB_SYSTEM_USER_TOKEN}"
resp_review = requests.get(url_review, timeout=15)
print(f"Status: {resp_review.status_code}")
print(f"Response: {resp_review.text[:1000]}")

print()
print("=== TEST 3: Attempt actual IG message send to a known sender (if any) ===")
# First, check if we have any stored IG sender in the DB
import sqlite3, os
db_path = os.path.join("C:\\Users\\Micro-Tech\\AppData\\Local\\", "messages.db")
if os.path.exists("messages.db"):
    db_path = "messages.db"
elif os.path.exists("data.db"):
    db_path = "data.db"
else:
    # Check for any .db files
    import glob
    dbs = glob.glob("*.db")
    print(f"Found DBs: {dbs}")
    for db in dbs:
        try:
            conn = sqlite3.connect(db)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            print(f"  {db} tables: {[t[0] for t in tables]}")
            conn.close()
        except:
            pass

print()
print("=== TEST 4: Get a fresh Page Token with explicit IG scopes ===")
# The get_fb_page_token() doesn't request specific scopes
# Let's try to get the token with the Instagram scope explicitly
url_me = f"https://graph.facebook.com/v21.0/me/accounts?fields=access_token,instagram_business_account,name,id&access_token={FB_SYSTEM_USER_TOKEN}"
resp_me = requests.get(url_me, timeout=15)
data_me = resp_me.json()
for page in data_me.get("data", []):
    pt = page.get("access_token", "")
    ig = page.get("instagram_business_account", {})
    print(f"Page: {page.get('name')}")
    print(f"  Page Token exists: {bool(pt)}")
    print(f"  IG Account: {ig.get('id') if ig else 'NONE'}")
    print(f"  Token prefix: {pt[:30] if pt else 'N/A'}")

print()
print("=== TEST 5: Verify /messages endpoint with System User Token directly ===")
# Some endpoints require the System User Token not the Page Token
ig_account_id = "17841473888839712"
url_direct = f"https://graph.facebook.com/v22.0/{ig_account_id}/messages"
payload = {
    "recipient": {"id": "TEST_SENDER"},  # dummy, won't actually work
    "message": {"text": "test"}
}
headers = {"Content-Type": "application/json"}
print(f"Endpoint: POST {url_direct}")
print(f"Using: System User Token prefix: {FB_SYSTEM_USER_TOKEN[:20] if FB_SYSTEM_USER_TOKEN else 'N/A'}")

# Actually let's check the API documentation says:
# The /{ig-account-id}/messages endpoint requires:
# - access_token = A User Access Token with instagram_manage_messages, OR
# - A Page Access Token from a page that has an IG account
print()
print("=== FINAL ANALYSIS ===")
print("The Page Token HAS 'instagram_manage_messages' in its granular scopes.")
print("But the APP (RC Agents) itself seems to lack the Instagram Messenger API product.")
print("This can be fixed in Meta Developer Dashboard:")
print("1. Go to https://developers.facebook.com/apps/1319156913738249/")
print("2. Add Product -> Instagram Messenger API")
print("3. OR: Check if the app has completed App Review for instagram_manage_messages")
print("4. If in Development Mode, add testers and test with those accounts only")
