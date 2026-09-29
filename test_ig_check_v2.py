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

params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': sys_token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
data = resp.json()
page_token = data['data'][0]['access_token']

print("=== CHECKING CONVERSATIONS ===")
conv_url = 'https://graph.facebook.com/v25.0/me/conversations'
conv_params = {
    'fields': 'id,participants,messages.limit(1){message,from,created_time},updated_time',
    'access_token': page_token
}
resp_c = requests.get(conv_url, params=conv_params, timeout=15)

if resp_c.status_code == 200:
    convs = resp_c.json().get('data', [])
    print(f"Total conversations: {len(convs)}")
    
    sorted_c = sorted(convs, key=lambda c: c.get('updated_time', ''), reverse=True)
    
    for conv in sorted_c[:5]:
        updated = conv.get('updated_time', '?')[:19]
        msgs = conv.get('messages', {}).get('data', [])
        parts = conv.get('participants', {}).get('data', [])
        part_ids = [p.get('id') for p in parts if p.get('id') != '1040729219115342']
        
        if msgs:
            m = msgs[0]
            txt = str(m.get('message', ''))[:80]
            from_name = m.get('from', {}).get('name', '?')
            print(f"  [{updated}] {from_name} ({part_ids[0][:25]}): {txt}")
        else:
            print(f"  [{updated}] No msgs parts={part_ids}")
    
    # If new conversations appeared
    if len(convs) > 9:
        print()
        print(f"NEW CONVERSATION! Count went from 9 to {len(convs)}")
        
        new_conv = sorted_c[0]
        nid = [p.get('id') for p in new_conv.get('participants', {}).get('data', []) if p.get('id') != '1040729219115342']
        
        if nid:
            sid = nid[0]
            
            # Try 1: IG endpoint
            print()
            print("=== TRYING /{ig_id}/messages ===")
            url1 = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/messages'
            payload = {
                'recipient': {'id': sid},
                'message': {'text': 'مرحبا! رد آلي من Royal Chaussures ✅ تم استلام رسالتك بنجاح!'}
            }
            headers = {'Content-Type': 'application/json'}
            send_params = {'access_token': page_token}
            
            r1 = requests.post(url1, params=send_params, json=payload, headers=headers, timeout=15)
            print(f"Status: {r1.status_code}")
            print(f"Response: {r1.text[:300]}")
            
            if r1.status_code == 200:
                print()
                print("🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉")
                print("  INSTAGRAM DM SENT! 🎉")
                print("🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉")
            else:
                # Try 2: /me/messages
                print()
                print("=== TRYING /me/messages ===")
                url2 = 'https://graph.facebook.com/v25.0/me/messages'
                r2 = requests.post(url2, params=send_params, json=payload, headers=headers, timeout=15)
                print(f"Status: {r2.status_code}")
                print(f"Response: {r2.text[:300]}")
    else:
        print()
        print("Still 9 conversations - tester message not received yet.")
        print()
        print("Try sending a fresh DM from @ahmeddd___tlm to @royal.chaussures.dz")
        print("on Instagram app, then re-run this script.")
else:
    print(f"Error: {resp_c.text[:300]}")
