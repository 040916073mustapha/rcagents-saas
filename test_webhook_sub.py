import os
import requests
import json

# Read .env manually
env_vars = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            env_vars[key.strip()] = val.strip()

sys_token = env_vars.get('FB_SYSTEM_USER_TOKEN', '')
ig_account_id = "17841473888839712"

# Get Page Token
params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': sys_token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
data = resp.json()
page_token = data['data'][0]['access_token']

print('=== CHECK WEBHOOK SUBSCRIPTIONS ===')
# Check what webhooks the IG account is subscribed to
url_subs = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/subscribed_apps'
subs_params = {'access_token': page_token}
resp_subs = requests.get(url_subs, params=subs_params, timeout=15)
print(f'IG subscribed apps: Status {resp_subs.status_code}')
if resp_subs.status_code == 200:
    print(json.dumps(resp_subs.json(), indent=2)[:500])
else:
    print(f'Error: {resp_subs.text[:400]}')

print()
print('=== CHECK PAGE SUBSCRIPTIONS ===')
page_id = '1040729219115342'
url_page_subs = 'https://graph.facebook.com/v25.0/' + page_id + '/subscribed_apps'
resp_ps = requests.get(url_page_subs, params=subs_params, timeout=15)
print(f'Page subscribed apps: Status {resp_ps.status_code}')
if resp_ps.status_code == 200:
    apps = resp_ps.json().get('data', [])
    for app in apps:
        print(f'  App: {app.get("name")}')
        print(f'  Fields: {app.get("subscribed_fields")}')
else:
    print(f'Error: {resp_ps.text[:400]}')

print()
print('=== CHECK WHAT WEBHOOK ENDPOINT META HAS ===')
# The webhook endpoint URL is at Meta Developers level, not accessible via API
# But we can check what the app's webhook config looks like
app_id = '1319156913738249'
url_app = 'https://graph.facebook.com/v25.0/' + app_id
app_params = {'fields': 'name,link,app_domains,app_type', 'access_token': sys_token}
resp_app = requests.get(url_app, params=app_params, timeout=15)
if resp_app.status_code == 200:
    app_data = resp_app.json()
    print(f'  App Name: {app_data.get("name")}')
    print(f'  Link: {app_data.get("link")}')
    print(f'  Domains: {app_data.get("app_domains")}')
else:
    print(f'Error: {resp_app.text[:300]}')

print()
print('=== What I need from you ===')
print('1. Did you send the DM from the INSTAGRAM app (not Facebook Messenger)?')
print('2. If yes, check if the @royal.chaussures.dz account received a notification')
print('3. If notification appears, the webhook should fire and we can reply')
print()
print('=== Alternative: Check via send_ig_reply simulation ===')
print('We can try a direct test if you give me a sender IGSID')
print('For now, try sending a DM from INSTAGRAM app to @royal.chaussures.dz')
print('Say anything like: Salam, test 🧪')
