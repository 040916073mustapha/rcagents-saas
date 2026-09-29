import requests, json, hmac, hashlib

# === CONFIG ===
APP_SECRET = "d8b1ed95d3a735dc7f8bb3b4e3b1b4c1"
WEBHOOK_URL = "https://app.rcagents.space/webhook"

# === Simulate a realistic Instagram webhook payload ===
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

# === Step 1: Get the exact raw bytes the server will receive ===
# We json.dumps first to get the exact byte representation
body_bytes = json.dumps(payload_dict, ensure_ascii=True, separators=(',', ':')).encode('utf-8')

print(f"=== DEBUG: Body bytes ({len(body_bytes)} bytes) ===")
print(f"Body repr: {body_bytes[:200]}...")

# === Step 2: Compute HMAC as Meta would ===
# Meta uses the EXACT raw POST body with separators=(',', ':')
expected_sig = "sha256=" + hmac.new(
    APP_SECRET.encode("utf-8"),
    body_bytes,
    hashlib.sha256
).hexdigest()

print(f"\nComputed signature: {expected_sig}")

# === Step 3: Send with the CORRECT signature header ===
headers = {
    "Content-Type": "application/json",
    "X-Hub-Signature-256": expected_sig
}

print(f"\n=== Sending to {WEBHOOK_URL} ===")
print(f"Header X-Hub-Signature-256: {expected_sig}")
print(f"Body size: {len(body_bytes)} bytes")

resp = requests.post(WEBHOOK_URL, data=body_bytes, headers=headers, timeout=10)
print(f"\nResponse Status: {resp.status_code}")
print(f"Response Body: {resp.text[:300]}")

if resp.status_code == 200:
    print("\n✅ SUCCESS! Signature verification passed!")
else:
    print(f"\n❌ FAILED with {resp.status_code}")
