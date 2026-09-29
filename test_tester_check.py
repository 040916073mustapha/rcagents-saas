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

print('Token found:', bool(sys_token))
print('Token prefix:', sys_token[:15])

# Get Page Token
params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': sys_token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
data = resp.json()
page_token = data['data'][0]['access_token']
print('Page Token prefix:', page_token[:15])
print()

# Check conversations for any new tester messages
print('=== CHECKING ALL CONVERSATIONS ===')
conv_url = 'https://graph.facebook.com/v25.0/me/conversations'
conv_params = {'fields': 'id,participants,messages.limit(3){message,from,created_time}', 'access_token': page_token}
resp_c = requests.get(conv_url, params=conv_params, timeout=15)

if resp_c.status_code == 200:
    convs = resp_c.json().get('data', [])
    print('Total conversations:', len(convs))
    
    for conv in convs[:10]:
        conv_id = conv.get('id')
        msgs = conv.get('messages', {}).get('data', [])
        parts = conv.get('participants', {}).get('data', [])
        part_ids = [p.get('id') for p in parts if p.get('id') != '1040729219115342']
        
        if msgs:
            last = msgs[-1]
            from_name = last.get('from', {}).get('name', '?')
            from_id = last.get('from', {}).get('id', '?')
            text = str(last.get('message', ''))[:100]
            time = last.get('created_time', '?')
            print()
            print(f'  Conv: {conv_id}')
            print(f'  Participants: {part_ids}')
            print(f'  Last msg: [{time}] {from_name} ({from_id[:20]}): {text}')
else:
    print('Error:', resp_c.text[:400])

print()
print('=== TO TEST IG DM ===')
print('1. Send a DM from @ahmeddd___tlm to @royal.chaussures.dz')
print('2. Say: "Hello test from tester"')
print('3. Then run this script again')
print()
print('=== OR: Try to find tester by FB user lookup ===')
# Try looking up the tester account by their IG username
ig_test_username = 'ahmeddd___tlm'

# Try to search for the IG account
url_search = 'https://graph.facebook.com/v21.0/' + ig_account_id
search_params = {
    'fields': 'name,username,business_discovery.username(' + ig_test_username + '){id,username,name}',
    'access_token': page_token
}
resp_search = requests.get(url_search, params=search_params, timeout=15)
print(f'Business discovery result: {resp_search.status_code}')
if resp_search.status_code == 200:
    print(json.dumps(resp_search.json(), indent=2)[:500])
else:
    print(f'Error: {resp_search.text[:300]}')

print()
print('Alternatively, try GET /{ig_id}/messages with a direct payload')
print('The tester @ahmeddd___tlm must DM first for us to get their IGSID')
