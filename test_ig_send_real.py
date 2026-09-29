import re
import requests
import json

with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'FB_SYSTEM_USER_TOKEN=(.+)', content)
sys_token = match.group(1).strip()

# Get Page Token
params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': sys_token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
data = resp.json()
page_token = data['data'][0]['access_token']
ig_account_id = data['data'][0]['instagram_business_account']['id']
page_id = data['data'][0]['id']

# Known IG participant IDs from conversations
# These are IGSID (Instagram Scoped IDs) - start with 276/277
# They are from FB Page conversations, which could be FB or IG
# Let's try to determine which ones are IG

# Try sending to one of these IDs via /{ig_account_id}/messages
print('=== TEST 1: Try /me/messages endpoint (works for both FB + IG) ===')
# This is the standard way to send DMs
# For IG: the sender_id MUST be an IGSID (starts with 2xxxxxxxxx)
test_sender = '27698473049760867'  # First conversation participant
send_url = 'https://graph.facebook.com/v25.0/me/messages'
send_payload = {
    'recipient': {'id': test_sender},
    'message': {'text': 'Hello! This is a test from RC Agents bot. If you receive this, IG messaging is working!'}
}
send_headers = {'Content-Type': 'application/json'}
send_params = {'access_token': page_token}

print('Sending via /me/messages to:', test_sender)
resp_send = requests.post(send_url, params=send_params, json=send_payload, headers=send_headers, timeout=15)
print('Status:', resp_send.status_code)
print('Response:', resp_send.text[:500])

# If that doesn't work, try /{ig_account_id}/messages
if resp_send.status_code != 200:
    print()
    print('=== TEST 2: Try /{ig_account_id}/messages ===')
    send_url2 = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/messages'
    resp_send2 = requests.post(send_url2, params=send_params, json=send_payload, headers=send_headers, timeout=15)
    print('Status:', resp_send2.status_code)
    print('Response:', resp_send2.text[:500])

# Check if the conversation participants include the page in multiple conversations
print()
print('=== TEST 3: Check conversation types ===')
for conv_id in ['t_1645685369988838', 't_1069439532656674']:
    url = 'https://graph.facebook.com/v25.0/' + conv_id
    conv_params = {'fields': 'id,participants,messages.limit(1){message,from}', 'access_token': page_token}
    resp_c = requests.get(url, params=conv_params, timeout=15)
    if resp_c.status_code == 200:
        cdata = resp_c.json()
        msgs = cdata.get('messages', {}).get('data', [])
        print('  Conversation:', conv_id)
        if msgs:
            print('    Last message from:', msgs[0].get('from'))
            print('    Text:', str(msgs[0].get('message', ''))[:100])
        parts = cdata.get('participants', {}).get('data', [])
        print('    All participants:', [p.get('id') for p in parts])
