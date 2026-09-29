import re
import requests
import json

with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'FB_SYSTEM_USER_TOKEN=(.+)', content)
sys_token = match.group(1).strip()

params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': sys_token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
data = resp.json()
page_token = data['data'][0]['access_token']
ig_account_id = data['data'][0]['instagram_business_account']['id']

# Get all conversations
print('=== Get ALL conversations with participant details ===')
conv_url = 'https://graph.facebook.com/v25.0/me/conversations'
conv_params = {'fields': 'id,participants,messages.limit(1){message,from}', 'access_token': page_token}
resp_c = requests.get(conv_url, params=conv_params, timeout=15)

if resp_c.status_code == 200:
    convs = resp_c.json().get('data', [])
    for conv in convs:
        parts = conv.get('participants', {}).get('data', [])
        msgs = conv.get('messages', {}).get('data', [])
        # Find non-page participants (those that aren't 10407...)
        for p in parts:
            pid = p.get('id', '')
            if pid != '1040729219115342':
                # Check if this looks like IGSID (Instagram IDs are often shorter than FB PSIDs)
                print('Participant:', pid, '   length:', len(pid))
                print('  Looks like IGSID:', pid.startswith('276') or pid.startswith('277') or pid.startswith('269') or pid.startswith('271') or pid.startswith('272'))
                if msgs:
                    last_msg = msgs[0].get('message', '')
                    last_from = msgs[0].get('from', {}).get('name', 'N/A')
                    print('  Last msg from:', last_from, ':', str(last_msg)[:80])

# Now try to send via the IG-specific endpoint
print()
print('=== Now try: POST /{ig_account_id}/messages with IGSID ===')
# Find a participant that might be IG
for conv in convs:
    parts = conv.get('participants', {}).get('data', [])
    for p in parts:
        pid = p.get('id', '')
        if pid != '1040729219115342':
            # Try the IG endpoint
            send_url = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/messages'
            send_payload = {
                'recipient': {'id': pid},
                'message': {'text': '🌟 Test from RC Agents via IG endpoint! Do you receive this?'}
            }
            headers = {'Content-Type': 'application/json'}
            params_send = {'access_token': page_token}
            print('  Trying to send to:', pid, 'via IG endpoint')
            resp_s = requests.post(send_url, params=params_send, json=send_payload, headers=headers, timeout=15)
            print('  Status:', resp_s.status_code)
            print('  Response:', resp_s.text[:400])
            break  # Only try first one
    break  # Only try first conversation
