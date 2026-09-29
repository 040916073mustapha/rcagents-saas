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

print('Page Token prefix:', page_token[:15])

# Get full conversation list with details
print()
print('=== ALL CONVERSATIONS WITH LATEST 2 MESSAGES ===')
conv_url = 'https://graph.facebook.com/v25.0/me/conversations'
conv_params = {
    'fields': 'id,participants,messages.limit(2){message,from,created_time}',
    'access_token': page_token
}
resp_c = requests.get(conv_url, params=conv_params, timeout=15)

newest_sender_id = None
newest_time = ''

if resp_c.status_code == 200:
    convs = resp_c.json().get('data', [])
    print(f'Total: {len(convs)} conversations')
    
    for conv in convs:
        conv_id = conv.get('id')
        msgs = conv.get('messages', {}).get('data', [])
        parts = conv.get('participants', {}).get('data', [])
        
        # Get non-page participants
        part_ids = [p.get('id') for p in parts if p.get('id') != '1040729219115342']
        
        if msgs:
            for m in msgs:
                from_name = m.get('from', {}).get('name', '?')
                from_id = m.get('from', {}).get('id', '?')
                text = str(m.get('message', ''))[:120]
                msg_time = m.get('created_time', '')
                
                # Track newest message
                if msg_time > newest_time:
                    newest_time = msg_time
                    if from_id != '1040729219115342':  # Not from our page
                        newest_sender_id = from_id
                
                print(f'  [{msg_time[:19]}] {from_name} ({from_id[:25]}): {text}')
            print()
else:
    print('Error:', resp_c.text[:400])

if newest_sender_id:
    print(f'=== NEWEST SENDER (tester): {newest_sender_id} ===')
    print()
    
    # TRY Sending via IG endpoint now that tester is added
    print('=== TRYING: POST /v25.0/{ig_id}/messages ===')
    send_url = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/messages'
    send_payload = {
        'recipient': {'id': newest_sender_id},
        'message': {'text': '🌟 مرحباً! هذا اختبار من RC Agents بوت. هل تستقبل هذه الرسالة؟ ✅'}
    }
    headers = {'Content-Type': 'application/json'}
    params_send = {'access_token': page_token}
    
    resp_s = requests.post(send_url, params=params_send, json=send_payload, headers=headers, timeout=15)
    print(f'Status: {resp_s.status_code}')
    print(f'Response: {resp_s.text[:600]}')
    
    if resp_s.status_code == 200:
        print()
        print('🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅')
        print('  INSTAGRAM DM SENT SUCCESSFULLY!')
        print('🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅🎉✅')
    else:
        # Try /me/messages alternative
        print()
        print('=== TRYING ALTERNATIVE: POST /v25.0/me/messages ===')
        send_url2 = 'https://graph.facebook.com/v25.0/me/messages'
        resp_s2 = requests.post(send_url2, params=params_send, json=send_payload, headers=headers, timeout=15)
        print(f'Status: {resp_s2.status_code}')
        print(f'Response: {resp_s2.text[:600]}')
else:
    print('No new message found. The tester may not have sent from IG yet.')
