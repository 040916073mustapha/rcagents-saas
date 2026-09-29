import requests, json, hmac, hashlib

APP_SECRET = "d8b1ed95d3a735dc7f8bb3b4e3b1b4c1"
WEBHOOK_URL = "https://app.rcagents.space/webhook"

# Simulate EXACT payload from Meta with Instagram test event
# Meta uses Python's default json.dumps order (insertion order)
# BUT the key is: Meta serializes with compact separators (no spaces)
payload_dict = {
    "object": "instagram",
    "entry": [{
        "id": "17841473888839712",
        "time": 1695200000,
        "messaging": [{
            "sender": {"id": "1234567890"},
            "recipient": {"id": "17841473888839712"},
            "timestamp": 1695200000,
            "message": {
                "mid": "mid_test_1",
                "text": "Bonjour, combien coute cette chaussure?"
            }
        }]
    }]
}

print("=== CRITICAL TEST: Meta uses sort_keys? ===")
# Some older JSON libs use different key ordering
body_no_sort = json.dumps(payload_dict, ensure_ascii=True, separators=(',', ':')).encode()
body_sorted = json.dumps(payload_dict, ensure_ascii=True, separators=(',', ':'), sort_keys=True).encode()

print(f"Without sort_keys: {body_no_sort}")
print(f"With sort_keys:    {body_sorted}")
print(f"Same? {body_no_sort == body_sorted}")

sig_no_sort = "sha256=" + hmac.new(APP_SECRET.encode(), body_no_sort, hashlib.sha256).hexdigest()
sig_sorted = "sha256=" + hmac.new(APP_SECRET.encode(), body_sorted, hashlib.sha256).hexdigest()

print(f"\nSig (no sort): {sig_no_sort}")
print(f"Sig (sorted):  {sig_sorted}")
print(f"Same? {sig_no_sort == sig_sorted}")

# Now send sorted version
print(f"\n=== Sending SORTED version ===")
headers = {"Content-Type": "application/json", "X-Hub-Signature-256": sig_sorted}
resp = requests.post(WEBHOOK_URL, data=body_sorted, headers=headers, timeout=10)
print(f"Status: {resp.status_code} - {resp.text}")

# And without sort
print(f"\n=== Sending NON-SORTED version ===")
headers2 = {"Content-Type": "application/json", "X-Hub-Signature-256": sig_no_sort}
resp2 = requests.post(WEBHOOK_URL, data=body_no_sort, headers=headers2, timeout=10)
print(f"Status: {resp2.status_code} - {resp2.text}")

print()
print("=== THEORY: Flask get_data returns different body ===")
# What if the webhook server code has the issue?
# Let's send via requests.post(json=...) AND compute sig on what requests actually sends
body_of_requests = json.dumps(payload_dict, ensure_ascii=True).encode()
sig_of_requests = "sha256=" + hmac.new(APP_SECRET.encode(), body_of_requests, hashlib.sha256).hexdigest()
print(f"requests.post(json=...) sends:\n{body_of_requests[:200]}...")
print(f"\nSig for this body: {sig_of_requests}")
headers3 = {"Content-Type": "application/json", "X-Hub-Signature-256": sig_of_requests}
resp3 = requests.post(WEBHOOK_URL, data=body_of_requests, headers=headers3, timeout=10)
print(f"Status: {resp3.status_code} - {resp3.text}")
