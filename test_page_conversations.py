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

print('Page token prefix:', page_token[:15])
print('IG Account ID:', ig_account_id)
print('Page ID:', page_id)
print()

# TEST: What does /me/messages endpoint give us?
# According to Meta docs: POST /me/messages with page_token
# Works for both FB Messenger AND Instagram IF the token has IG scope
# BUT the key is the recipient.id must be an IG-scoped PSID

# Check what conversations we can access via PAGE ID (not IG account ID)
print('=== TEST A: GET /me/conversations (Page conversations) ===')
conv_params = {'fields': 'id,participants', 'access_token': page_token}
resp_c = requests.get('https://graph.facebook.com/v25.0/me/conversations', params=conv_params, timeout=15)
print('Status:', resp_c.status_code)
if resp_c.status_code == 200:
    convs = resp_c.json().get('data', [])
    print('  Conversations:', len(convs))
    for c in convs[:5]:
        print('  - ID:', c.get('id'))
        print('    Participants:', [p.get('id') for p in c.get('participants', {}).get('data', [])])
else:
    print('  Error:', resp_c.text[:400])

# Check Page inbox
print()
print('=== TEST B: Get /{page_id}/conversations ===')
conv_url = 'https://graph.facebook.com/v25.0/' + page_id + '/conversations'
conv_params2 = {'fields': 'id,participants,messages.limit(1){message}', 'access_token': page_token}
resp_c2 = requests.get(conv_url, params=conv_params2, timeout=15)
print('Status:', resp_c2.status_code)
if resp_c2.status_code == 200:
    convs2 = resp_c2.json().get('data', [])
    print('  Conversations:', len(convs2))
    for c in convs2[:5]:
        print('  - ID:', c.get('id'))
        parts = c.get('participants', {}).get('data', [])
        print('    Participants:', [p.get('id') for p in parts])
else:
    print('  Error:', resp_c2.text[:400])

# Try to find any IG conversations via the messages table
print()
print('=== TEST C: Check DB for any IG sender_ids ===')
import sqlite3
try:
    conn = sqlite3.connect('royal_orders.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT sender_id FROM messages WHERE platform="instagram"')
    senders = c.fetchall()
    print('  IG senders in DB:', [s[0][:30] for s in senders])
    conn.close()
except:
    print('  Could not check DB')
