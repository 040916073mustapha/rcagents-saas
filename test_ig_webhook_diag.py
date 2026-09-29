import os, requests, json

env_vars = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            env_vars[key.strip()] = val.strip()

sys_token = env_vars.get('FB_SYSTEM_USER_TOKEN', '')
app_id = "1319156913738249"

print("=== CHECK 1: Does Meta even try to send IG webhooks? ===")
# Check the app's webhook configuration
# Get the app's subscribed fields
url_app = 'https://graph.facebook.com/v25.0/' + app_id
params_app = {
    'fields': 'name,link,app_domains',
    'access_token': sys_token
}
resp_app = requests.get(url_app, params=params_app, timeout=15)
print(f"App info: {resp_app.status_code}")
if resp_app.status_code == 200:
    print(json.dumps(resp_app.json(), indent=2)[:300])

print()
print("=== CHECK 2: What fields is the app subscribed to for IG? ===")
# Check the app's webhook subscriptions
url_subs = 'https://graph.facebook.com/v25.0/' + app_id + '/subscriptions'
params_subs = {'access_token': sys_token}
resp_subs = requests.get(url_subs, params=params_subs, timeout=15)
print(f"App subscriptions: {resp_subs.status_code}")
if resp_subs.status_code == 200:
    data = resp_subs.json()
    print(json.dumps(data, indent=2)[:800])
else:
    print(f"Error: {resp_subs.text[:500]}")

print()
print("=== CHECK 3: Verify IG webhook endpoint is correctly configured ===")
# The webhook needs to be registered at:
# GET /{app_id}/subscriptions -> returns the configured callback URL
# But sometimes it's at the app level, not page/ig level

# Let's check the page subscriptions again with more detail
params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': sys_token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
data = resp.json()
page_token = data['data'][0]['access_token']
page_id = data['data'][0]['id']
ig_id = data['data'][0]['instagram_business_account']['id']

print("=== CHECK 4: Page subscribed apps (detailed) ===")
ps_url = 'https://graph.facebook.com/v25.0/' + page_id + '/subscribed_apps'
ps_params = {'access_token': page_token}
resp_ps = requests.get(ps_url, params=ps_params, timeout=15)
print(f"Status: {resp_ps.status_code}")
if resp_ps.status_code == 200:
    apps = resp_ps.json().get('data', [])
    for a in apps:
        print(f"  App: {a.get('name')} ({a.get('id')})")
        print(f"  Category: {a.get('category')}")
        print(f"  Link: {a.get('link')}")
        print(f"  Subscribed fields: {a.get('subscribed_fields')}")

print()
print("=== CHECK 5: Does the app have the correct webhook endpoint? ===")
# The app needs to have the webhook registered for both:
# - Page subscriptions (page + messages)
# - Instagram subscriptions (instagram + messages, messaging_postbacks)
# We can verify this by seeing if the IG account has any subscription at all

print("=== CHECK 6: Test if IG webhook would receive a message ===")
# We can simulate what Meta does: send a test webhook event
# But first, let's verify IG subscription at the IG account level
# The subscription was done at the PAGE level, not IG level
# Let's check if we can subscribe IG directly via POST

# Try to subscribe IG account again - the key is the access_token
# For IG subscription, we need the PAGE token, not system user token
print()
print("=== CHECK 7: Attempt IG subscription with proper token ===")
ig_sub_url = 'https://graph.facebook.com/v25.0/' + ig_id + '/subscribed_apps'
ig_sub_payload = {
    'subscribed_fields': 'messages,messaging_postbacks',
    'access_token': page_token
}
resp_ig_sub = requests.post(ig_sub_url, data=ig_sub_payload, timeout=15)
print(f"IG Subscribe: Status {resp_ig_sub.status_code}")
print(f"Response: {resp_ig_sub.text[:400]}")

print()
print("=== DIAGNOSIS ===")
print("The most likely cause the webhook doesn't fire is:")
print("The subscription was done on the PAGE, not the IG BUSINESS ACCOUNT.")
print()
print("From Meta Dashboard, try:")
print("1. Go to: Instagram > Webhooks > Instagram Subscriptions")
print("2. Verify it shows '@royal.chaussures.dz' as subscribed")
print("3. If not, add it with:")
print("   - IG Business Account ID: 17841473888839712")
print("   - Fields: messages, messaging_postbacks")
print("   - Callback URL: https://app.rcagents.space/webhook")
print("   - Verify Token: ROYAL-ROYAL-CH2026")
