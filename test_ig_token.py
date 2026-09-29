import requests, json

IG_TOKEN = 'EAASvxCcZCEgkBSgHZCdIkClUb4PRFrT6ia9NAAp1ZCzYVW0YnT6cBHknEzEcaIs3THpcdF5yl6xd7MZBdCuxeT4IWsiF0xE6JoKDdFSzDDU10WS0KZBmsGnSNAtyK4pZBZBkIfrNCekZAIhEPZCxA3yrkfFtqZCBJhNZBJlVaVoBlnAzXOdfvrjZAuAbQ2juMPwB1gZDZD'

print('=== TEST 1: Token Info (/me) ===')
try:
    url = f'https://graph.facebook.com/v22.0/me?access_token={IG_TOKEN}'
    resp = requests.get(url, timeout=10)
    print(f'Status: {resp.status_code}')
    data = resp.json()
    print(json.dumps(data, indent=2)[:500])
except Exception as e:
    print(f'Error: {e}')

print()
print('=== TEST 2: Instagram Business Account ===')
try:
    url = f'https://graph.facebook.com/v22.0/me/accounts?access_token={IG_TOKEN}'
    resp = requests.get(url, timeout=10)
    print(f'Status: {resp.status_code}')
    data = resp.json()
    print(json.dumps(data, indent=2)[:800])
except Exception as e:
    print(f'Error: {e}')

print()
print('=== TEST 3: Send DM via /me/messages ===')
try:
    url = f'https://graph.facebook.com/v22.0/me/messages?access_token={IG_TOKEN}'
    payload = {
        'recipient': {'id': '1234567890'},
        'message': {'text': 'Test from Louve via API'}
    }
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f'Status: {resp.status_code}')
    data = resp.json()
    print(json.dumps(data, indent=2)[:500])
except Exception as e:
    print(f'Error: {e}')
