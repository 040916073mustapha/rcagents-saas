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

print("=== CHECK CONVERSATIONS FOR NEW ONES ===")
conv_url = 'https://graph.facebook.com/v25.0/me/conversations'
conv_params = {
    'fields': 'id,participants,messages.limit(2){message,from,created_time},updated_time',
    'access_token': page_token
}
resp_c = requests.get(conv_url, params=conv_params, timeout=15)

if resp_c.status_code == 200:
    convs = resp_c.json().get('data', [])
    print(f"Total conversations: {len(convs)}")
    
    sorted_c = sorted(convs, key=lambda c: c.get('updated_time', ''), reverse=True)
    
    for conv in sorted_c[:5]:
        cid = conv.get('id')
        updated = conv.get('updated_time', '?')[:19]
        msgs = conv.get('messages', {}).get('data', [])
        parts = conv.get('participants', {}).get('data', [])
        part_ids = [p.get('id') for p in parts if p.get('id') != '1040729219115342']
        
        print(f"\n  [Updated: {updated}]")
        print(f"  Conv: {cid}")
        print(f"  Participants: {part_ids}")
        
        if msgs:
            for m in msgs:
                txt = str(m.get('message', ''))[:80]
                fname = m.get('from', {}).get('name', '?')
                fid = m.get('from', {}).get('id', '?')
                mtime = m.get('created_time', '?')[:19]
                print(f"  [{mtime}] {fname} ({fid[:25]}): {txt}")
    
    # Check if our tester appears in any conversation
    all_part_ids = set()
    for conv in convs:
        for p in conv.get('participants', {}).get('data', []):
            pid = p.get('id', '')
            if pid != '1040729219115342':
                all_part_ids.add(pid)
    
    print()
    print(f"All participant IDs: {list(all_part_ids)[:15]}")
    print(f"Tester IGSID ({tester_igsid}) in list: {tester_igsid in all_part_ids}")
    
    if tester_igsid in all_part_ids:
        print()
        print("🎯 TESTER FOUND IN CONVERSATIONS! Instagram DMs WORKING!")
else:
    print(f"Error: {resp_c.text[:300]}")
