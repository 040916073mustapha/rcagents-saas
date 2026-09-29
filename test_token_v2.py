import re
import requests
import json

with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'FB_SYSTEM_USER_TOKEN=(.+)', content)
token = match.group(1).strip()
print('Token prefix:', token[:15], '...')
print('Token length:', len(token))
print('Starts with EAAS:', token.startswith('EAAS'))

print()
print('=== TEST 1: Get Page Token ===')
params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
print('Status:', resp.status_code)
if resp.status_code == 200:
    data = resp.json()
    for page in data.get('data', []):
        pt = page.get('access_token', '')
        ig = page.get('instagram_business_account', {})
        print('  Page:', page.get('name'), '(', page.get('id'), ')')
        print('  IG:', ig.get('id'))
        print('  Page Token prefix:', pt[:15], '...')
        
        print()
        print('=== TEST 2: Token Debug ===')
        d_params = {'input_token': pt, 'access_token': token}
        resp_d = requests.get('https://graph.facebook.com/v21.0/debug_token', params=d_params, timeout=15)
        if resp_d.status_code == 200:
            d = resp_d.json().get('data', {})
            scopes = [s['scope'] for s in d.get('granular_scopes', [])]
            print('  Scopes:', scopes)
            has_ig = 'instagram_manage_messages' in scopes
            print('  Has instagram_manage_messages:', has_ig)
        
        print()
        print('=== TEST 3: Conversations API ===')
        ig_id = ig.get('id', '')
        conv_params = {'fields': 'id,participants', 'access_token': pt}
        resp_c = requests.get('https://graph.facebook.com/v25.0/' + ig_id + '/conversations', params=conv_params, timeout=15)
        print('Status:', resp_c.status_code)
        if resp_c.status_code == 200:
            convs = resp_c.json().get('data', [])
            print('  Conversations:', len(convs))
            for c in convs[:3]:
                print('  - ID:', c.get('id'))
        else:
            print('  Error:', resp_c.text[:400])
        
        print()
        print('=== VERDICT ===')
        if has_ig and resp_c.status_code == 200:
            print('  ✅ READY TO SEND! Instagram Messenger capability active!')
            print('  🎯 You can now send test messages from your IG account')
        elif has_ig:
            print('  ⚠️ Token has IG scope but Conversations API blocked')
            print('  → Check: App Mode = LIVE at Meta Dashboard')
        else:
            print('  ❌ Still missing instagram_manage_messages')
else:
    print('Error:', resp.text[:500])
