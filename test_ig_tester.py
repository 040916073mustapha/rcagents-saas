import re
import requests
import json

with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'FB_SYSTEM_USER_TOKEN=***', content)
sys_token = match.group(1).strip()
ig_account_id = "17841473888839712"

# Get Page Token
params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': sys_token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
data = resp.json()
page_token = data['data'][0]['access_token']

print('=== SENDING IG DM VIA /{ig_account_id}/messages ===')
print('Endpoint: POST /v25.0/' + ig_account_id + '/messages')

# First we need the IGSID of the tester.
# The tester's FB PSID can be found from /me/conversations
# But for Instagram-specific: the tester needs to send a DM first
# OR we can get their ID via the /{ig_id}/conversations endpoint
# Since we can't access conversations API, let's try sending via known ID

# We need to get the tester's IG-scoped ID. Let's try to figure it out
# by getting the tester user info

# Actually, let's search for the tester @ahmeddd___tlm
# First, let's test the endpoint with a generic approach

# According to Meta: after adding IG tester, the tester can receive DMs
# BUT the user still needs to initiate a conversation (send a message first)
# OR we can try the /{ig_id}/messages endpoint with the tester's IG user ID

# The tester needs to DM the business account FIRST
# THEN we can reply using the sender_id from that message

# Let's check conversations again to see if any new one appeared
print()
print('=== CHECKING CONVERSATIONS FOR TESTER MSGS ===')
conv_url = 'https://graph.facebook.com/v25.0/me/conversations'
conv_params = {'fields': 'id,participants,messages.limit(2){message,from,created_time}', 'access_token': page_token}
resp_c = requests.get(conv_url, params=conv_params, timeout=15)

if resp_c.status_code == 200:
    convs = resp_c.json().get('data', [])
    print('Total conversations:', len(convs))
    for conv in convs:
        parts = conv.get('participants', {}).get('data', [])
        msgs = conv.get('messages', {}).get('data', [])
        part_ids = [p.get('id') for p in parts if p.get('id') != '1040729219115342']
        print('  Conv:', conv.get('id'))
        print('  Participants:', part_ids)
        if msgs:
            for m in msgs:
                m_from = m.get('from', {}).get('name', 'unknown')
                m_text = str(m.get('message', ''))[:80]
                m_time = m.get('created_time', '')
                print('    Msg from:', m_from, '|', m_text, '|', m_time)
else:
    print('Error:', resp_c.text[:300])

print()
print('=== HOW TO PROCEED ===')
print('1. From your @ahmeddd___tlm IG account, send a DM to @royal.chaussures.dz')
print('2. Say something like: "Hello test message"')
print('3. Wait 10-15 seconds for the webhook to fire')
print('4. Then run the test again to check the conversation')
print()
print('OR: We can try to look up the tester by their FB ID')
print('Do you have the tester user ID (starting with 2xx...) from FB?')
