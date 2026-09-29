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
tester_igsid = "1748973966270244"

params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': sys_token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
data = resp.json()
page_token = data['data'][0]['access_token']

print(f"Tester IGSID: {tester_igsid}")
print(f"IG Account ID: {ig_account_id}")
print()

# Method 1: /{ig_id}/messages (THE CORRECT IG ENDPOINT)
print("=== METHOD 1: POST /v25.0/{ig_id}/messages ===")
url1 = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/messages'
payload1 = {
    'recipient': {'id': tester_igsid},
    'message': {'text': '🌟 مرحباً @ahmeddd___tlm! هذا رد مباشر من RC Agents بوت عبر Instagram API ✅ تم استلام رسالتك وعملية الإرسال تعمل بنجاح! 🎉🚀'}
}
headers = {'Content-Type': 'application/json'}
send_params = {'access_token': page_token}

resp1 = requests.post(url1, params=send_params, json=payload1, headers=headers, timeout=15)
print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text[:500]}")

if resp1.status_code == 200:
    msg_id = resp1.json().get('message_id', 'N/A')
    print()
    print("🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉")
    print(f"  ✅ IG DM SENT! message_id: {msg_id}")
    print("  📱 Check @ahmeddd___tlm Instagram DMs!")
    print("🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉")
else:
    # Method 2: /me/messages
    print()
    print("=== METHOD 2: POST /v25.0/me/messages ===")
    url2 = 'https://graph.facebook.com/v25.0/me/messages'
    resp2 = requests.post(url2, params=send_params, json=payload1, headers=headers, timeout=15)
    print(f"Status: {resp2.status_code}")
    print(f"Response: {resp2.text[:500]}")
    
    if resp2.status_code == 200:
        msg_id = resp2.json().get('message_id', 'N/A')
        print()
        print("🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉")
        print(f"  ✅ IG DM SENT via /me/messages! msg_id: {msg_id}")
        print("  📱 Check @ahmeddd___tlm Instagram DMs!")
        print("🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉")
    else:
        print()
        print("Both methods failed. Error analysis:")
        print(resp1.text[:200])
