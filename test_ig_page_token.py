import requests, json

# The COMPLETE Page Access Token from Royal Chaussures Dz
PAGE_TOKEN = "EAASvxCcZCEgkBStUFwjRtQ5IYEl2LpTt1baQhelOeHkViKqNtBdApQtZAGKZBk7YJaNx8qPrixYWkZB14SKnDTVfMGgsWxVUyqNeSdDq3QBZBumjRTyZAkkco11YTrHJKIAmRljFNg5jXg4adPZAm9z1GBoZCtxdCJRACsLszuZBRe1ahlEfybEw6BTGqMurov3KRfLxX"

HEADERS = {
    "Content-Type": "application/json"
}

# Test A: Check conversations (to find real IG user IDs)
print("=== TEST A: Get Conversations ===")
try:
    url = f"https://graph.facebook.com/v22.0/1040729219115342/conversations?platform=instagram&access_token=***"
    resp = requests.get(url, timeout=10)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2)[:600])
except Exception as e:
    print(f"Error: {e}")

print()
print("=== TEST B: Send DM via /me/messages ===")
try:
    url = f"https://graph.facebook.com/v22.0/me/messages?access_token=***"
    payload = {
        "recipient": {"id": "1234567890"},
        "message": {"text": "Test DM from Louve via Page Token"}
    }
    resp = requests.post(url, json=payload, headers=HEADERS, timeout=10)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2)[:500])
except Exception as e:
    print(f"Error: {e}")

print()
print("=== TEST C: Check IG Business Account linked to Page ===")
try:
    url = f"https://graph.facebook.com/v22.0/1040729219115342?fields=instagram_business_account&access_token=***"
    resp = requests.get(url, timeout=10)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2)[:500])
except Exception as e:
    print(f"Error: {e}")

print()
print("=== TEST D: Send via IG-specific endpoint ===")
try:
    # The IG Business ID from Supabase
    IG_BUSINESS_ID = "17841473888839712"
    url = f"https://graph.facebook.com/v22.0/{IG_BUSINESS_ID}/messages?access_token=***"
    payload = {
        "recipient": {"id": "1234567890"},
        "message": {"text": "Test DM from Louve"}
    }
    resp = requests.post(url, json=payload, headers=HEADERS, timeout=10)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2)[:500])
except Exception as e:
    print(f"Error: {e}")
