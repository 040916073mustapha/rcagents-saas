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
tester_username = "ahmeddd___tlm"

# Get Page Token
params = {'fields': 'instagram_business_account,access_token,name,id', 'access_token': sys_token}
resp = requests.get('https://graph.facebook.com/v21.0/me/accounts', params=params, timeout=15)
data = resp.json()
page_token = data['data'][0]['access_token']

# Quick check: list ALL conversations with newest first, more details
print('=== FULL CONVERSATION CHECK (all 9 conversations with timestamps) ===')
conv_url = 'https://graph.facebook.com/v25.0/me/conversations'
conv_params = {
    'fields': 'id,participants,messages.limit(1){message,from,created_time},updated_time',
    'access_token': page_token
}
resp_c = requests.get(conv_url, params=conv_params, timeout=15)

if resp_c.status_code == 200:
    convs = resp_c.json().get('data', [])
    print(f'Total: {len(convs)} conversations')
    for conv in sorted(convs, key=lambda c: c.get('updated_time', ''), reverse=True):
        conv_id = conv.get('id')
        updated = conv.get('updated_time', '?')[:19]
        msgs = conv.get('messages', {}).get('data', [])
        parts = conv.get('participants', {}).get('data', [])
        part_ids = [p.get('id') for p in parts if p.get('id') != '1040729219115342']
        
        if msgs:
            m = msgs[0]
            txt = str(m.get('message', ''))[:80]
            from_name = m.get('from', {}).get('name', '?')
            from_id = m.get('from', {}).get('id', '?')
            msg_time = m.get('created_time', '?')[:19]
            print(f'  [{updated}] {from_name} ({from_id[:25]}): {txt}')
else:
    print(f'Error: {resp_c.text[:300]}')

print()
print('=== Searching for IG tester in ALL possible ways ===')

# Method 1: Try to find the IG user via our IG account's conversations (not page convs)
# Since /{ig_id}/conversations fails, let's try the page_scoped approach
# Method 2: Check if the tester is in the conversation participants
# Some IG conversations have different participant IDs
all_part_ids = set()
for conv in convs:
    for p in conv.get('participants', {}).get('data', []):
        pid = p.get('id', '')
        if pid != '1040729219115342':
            all_part_ids.add(pid)

print(f'All known participant IDs: {list(all_part_ids)}')
print(f'Count: {len(all_part_ids)}')

# Method 3: Try to find the tester via direct user lookup
print()
print('=== Trying to find tester user info ===')
# The tester when they DM from IG, their IGSID will be like these
# But if they DM from FB messenger, it will be a different ID
# Let's check all conversations more carefully - look for any new ones

# There's also a separate endpoint for IG conversations:
# GET /{ig_account_id}/conversations - we know this fails (#3)
# But maybe now that subscription is active, it might work?
print('=== Retry IG conversations (maybe now works?) ===')
conv_ig_url = 'https://graph.facebook.com/v25.0/' + ig_account_id + '/conversations'
conv_ig_params = {'fields': 'id,participants', 'access_token': page_token}
resp_igc = requests.get(conv_ig_url, params=conv_ig_params, timeout=15)
print(f'Status: {resp_igc.status_code}')
if resp_igc.status_code == 200:
    ig_convs = resp_igc.json().get('data', [])
    print(f'IG Conversations: {len(ig_convs)}')
    for c in ig_convs:
        print(f'  ID: {c.get("id")}')
else:
    print(f'Error: {resp_igc.text[:400]}')
