import os
import requests
import json

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

print('=== STEP 1: Subscribe IG account to webhook ===')
url = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/subscribed_apps'
payload = {
    'subscribed_fields': 'messages,messaging_postbacks',
    'access_token': page_token
}
headers = {'Content-Type': 'application/json'}

resp_sub = requests.post(url, json=payload, headers=headers, timeout=15)
print(f'Status: {resp_sub.status_code}')
if resp_sub.status_code == 200:
    result = resp_sub.json()
    print(f'✅ Success! Response: {json.dumps(result, indent=2)}')
    print()
    print('🎉🎉🎉 INSTAGRAM WEBHOOK SUBSCRIBED SUCCESSFULLY! 🎉🎉🎉')
    print('The bot will now receive Instagram DMs!')
else:
    print(f'❌ Error: {resp_sub.text[:500]}')
    
    # If page token doesn't work, try with system user token
    print()
    print('=== STEP 2: Retry with System User Token ===')
    payload2 = {
        'subscribed_fields': 'messages,messaging_postbacks',
        'access_token': sys_token
    }
    resp_sub2 = requests.post(url, json=payload2, headers=headers, timeout=15)
    print(f'Status: {resp_sub2.status_code}')
    if resp_sub2.status_code == 200:
        print(f'✅ Success with System Token! {json.dumps(resp_sub2.json(), indent=2)}')
        print()
        print('🎉🎉🎉 INSTAGRAM WEBHOOK SUBSCRIBED SUCCESSFULLY! 🎉🎉🎉')
    else:
        print(f'❌ Error with System Token: {resp_sub2.text[:500]}')
        print()
        print('=== STEP 3: Try subscription via Graph API with App-scoped token ===')
        # Sometimes the subscription needs to be done via the app's page token
        # using the POST method at the App level
        url_app = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/subscribed_apps'
        params3 = {
            'subscribed_fields': 'messages,messaging_postbacks',
            'access_token': sys_token  # System User Token may work here
        }
        resp_sub3 = requests.post(url_app, data=params3, timeout=15)
        print(f'Status: {resp_sub3.status_code}')
        print(f'Response: {resp_sub3.text[:500]}')
