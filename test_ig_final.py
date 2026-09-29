import os, requests, json

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

print('=== CONFIRM SUBSCRIPTION WORKED ===')
url_subs = 'https://graph.facebook.com/v25.0/me/subscribed_apps'
params_subs = {'access_token': page_token}
resp_subs = requests.get(url_subs, params=params_subs, timeout=15)
print(f'Page subscribed apps: Status {resp_subs.status_code}')
if resp_subs.status_code == 200:
    for app in resp_subs.json().get('data', []):
        print(f'  App: {app.get("name")}')
        print(f'  Fields: {app.get("subscribed_fields")}')

print()
print('=== CHECK ALL CONVERSATIONS LOOKING FOR TESTER MSG ===')
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
    print(f'Total conversations: {len(convs)}')
    
    # Check if new conversations appeared (10+ now)
    for conv in convs[-3:]:  # Check most recent conversations
        conv_id = conv.get('id')
        msgs = conv.get('messages', {}).get('data', [])
        parts = conv.get('participants', {}).get('data', [])
        
        part_ids = [p.get('id') for p in parts if p.get('id') != '1040729219115342']
        
        if msgs:
            for m in msgs:
                from_name = m.get('from', {}).get('name', '?')
                from_id = m.get('from', {}).get('id', '?')
                text = str(m.get('message', ''))[:100]
                msg_time = m.get('created_time', '')
                
                if msg_time > newest_time:
                    newest_time = msg_time
                    if from_id != '1040729219115342':
                        newest_sender_id = from_id
                
                print(f'  [{msg_time[:19]}] {from_name} ({from_id}): {text}')
    print()
else:
    print(f'Error: {resp_c.text[:400]}')

if newest_sender_id:
    print(f'=== NEWEST SENDER (tester?): {newest_sender_id} ===')
    
    # TRY sending a reply via IG endpoint
    print()
    print('=== SENDING IG DM REPLY VIA /{ig_id}/messages ===')
    send_url = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/messages'
    send_payload = {
        'recipient': {'id': newest_sender_id},
        'message': {'text': '🌟 مرحباً! هذا رد آلي من Royal Chaussures بوت. تم استلام رسالتك بنجاح ✅'}
    }
    headers = {'Content-Type': 'application/json'}
    send_params = {'access_token': page_token}
    
    resp_s = requests.post(send_url, params=send_params, json=send_payload, headers=headers, timeout=15)
    print(f'Status: {resp_s.status_code}')
    print(f'Response: {resp_s.text[:600]}')
    
    if resp_s.status_code == 200:
        msg_id = resp_s.json().get('message_id', '?')
        print()
        print('🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉')
        print(f'  IG DM SENT! message_id={msg_id}')
        print('🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉')
    else:
        print()
        print('=== TRYING /me/messages ALTERNATIVE ===')
        send_url2 = 'https://graph.facebook.com/v25.0/me/messages'
        resp_s2 = requests.post(send_url2, params=send_params, json=send_payload, headers=headers, timeout=15)
        print(f'Status: {resp_s2.status_code}')
        print(f'Response: {resp_s2.text[:600]}')
else:
    print('❌ No new messages from tester found.')
    print()
    print('Did you send the DM from Instagram app to @royal.chaussures.dz?')
    print('The tester @ahmeddd___tlm needs to DM the business account first.')
