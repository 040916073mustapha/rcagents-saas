import requests, json, hmac, hashlib

APP_SECRET = "d8b1ed95d3a735dc7f8bb3b4e3b1b4c1"
WEBHOOK_URL = "https://app.rcagents.space/webhook"

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

print("=== TEST 1: json.dumps with no separators (standard) ===")
body1 = json.dumps(payload_dict, ensure_ascii=True).encode('utf-8')
sig1 = "sha256=" + hmac.new(APP_SECRET.encode(), body1, hashlib.sha256).hexdigest()
print(f"Body: {body1[:120]}...")
print(f"Sig:  {sig1}")
headers1 = {"Content-Type": "application/json", "X-Hub-Signature-256": sig1}
r1 = requests.post(WEBHOOK_URL, data=body1, headers=headers1, timeout=10)
print(f"Status: {r1.status_code} - {r1.text}")

print()
print("=== TEST 2: json.dumps with compact separators ===")
body2 = json.dumps(payload_dict, ensure_ascii=True, separators=(',', ':')).encode('utf-8')
sig2 = "sha256=" + hmac.new(APP_SECRET.encode(), body2, hashlib.sha256).hexdigest()
print(f"Body: {body2[:120]}...")
print(f"Sig:  {sig2}")
headers2 = {"Content-Type": "application/json", "X-Hub-Signature-256": sig2}
r2 = requests.post(WEBHOOK_URL, data=body2, headers=headers2, timeout=10)
print(f"Status: {r2.status_code} - {r2.text}")

print()
print("=== TEST 3: requests.json= auto-serializes (what most senders do) ===")
# This is what Flask's request.get_data() sees when using requests.post(json=...)
sig3 = "sha256=" + hmac.new(APP_SECRET.encode(), body2, hashlib.sha256).hexdigest()
headers3 = {"Content-Type": "application/json", "X-Hub-Signature-256": sig3}
r3 = requests.post(WEBHOOK_URL, json=payload_dict, headers=headers3, timeout=10)
print(f"Using requests.post(json=...) (auto-serializes)")
print(f"Body sent: {r3.request.body[:120]}...")
print(f"Status: {r3.status_code} - {r3.text}")

print()
print("=== TEST 4: WITHOUT signature header (what FB Messenger does) ===")
r4 = requests.post(WEBHOOK_URL, json=payload_dict, timeout=10)
print(f"Status: {r4.status_code} - {r4.text}")

print()
print("=== TEST 5: Wrong signature (to confirm 403 behavior) ===")
headers5 = {"Content-Type": "application/json", "X-Hub-Signature-256": "sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
r5 = requests.post(WEBHOOK_URL, data=body1, headers=headers5, timeout=10)
print(f"Status: {r5.status_code} - {r5.text}")
