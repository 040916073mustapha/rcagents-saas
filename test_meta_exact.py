import requests, json, hmac, hashlib

APP_SECRET = "d8b1ed95d3a735dc7f8bb3b4e3b1b4c1"
WEBHOOK_URL = "https://app.rcagents.space/webhook"

# THE KEY INSIGHT: Meta uses the raw bytes of the POST body
# BUT there's a subtle issue with how the body is read

# Let me test: what if the server code has a bug with request body encoding?

# Test with different body formats that Meta might send
test_bodies = [
    # Format 1: Python json.dumps default (with spaces after separators)
    json.dumps({"object": "instagram", "entry": []}, ensure_ascii=True),
    # Format 2: No extra spaces
    json.dumps({"object": "instagram", "entry": []}, ensure_ascii=True, separators=(",", ":")),
]

print("=== Testing actual Meta body format ===\n")

# The key test: send WITHOUT Content-Type (Meta sometimes does this!)
print("--- TEST: Without Content-Type header ---")
body = json.dumps({"object": "instagram", "entry": [{"id": "17841473888839712", "time": 1695200000, "messaging": []}]}, ensure_ascii=True, separators=(",", ":")).encode()
sig = "sha256=" + hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
headers = {"X-Hub-Signature-256": sig}
resp = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=10)
print(f"Status: {resp.status_code} - {resp.text}")

print()
print("=== NOW THE REAL ISSUE ===")
print("The problem is likely this: Meta sends the payload with")
print("a specific JSON serialization. Let's check if the server")
print("code has the ACTUAL App Secret from Render env...")
print()
print("But wait - YOUR code change added .strip(), case-insensitive,")
print("and format validation. The 403 is still happening even after")
print("your changes. This means the signature mismatch is REAL,")
print("not a formatting issue.")
print()
print("The ONLY remaining possibility: THE PAYLOAD IS DIFFERENT")
print("between what Meta computed the signature on and what Flask")
print("receives. How?")
print()
print("1. Meta sends with sort_keys=True (alphabetical keys) - but our tests show this works")
print("2. Meta includes extra whitespace/newlines - but .strip() handles this")
print("3. Meta uses a different Content-Type like application/x-www-form-urlencoded")
print("4. Meta's JSON serialization differs from Python's")
print()
print("=== MOST LIKELY CULPRIT: Gzip/Content-Encoding ===")
print("Meta MAY send Content-Encoding: gzip but Flask decompresses")
print("before get_data(). Let's check if the server handles gzip...")
print()

# Check if server.py handles gzip
with open("server.py", "rb") as f:
    content = f.read()
    if b"gzip" in content.lower() or b"decompress" in content.lower() or b"content-encoding" in content.lower():
        print("Found gzip/content-encoding handling in server.py")
    else:
        print("NO gzip handling found in server.py!")
        print("If Meta sends Content-Encoding: gzip, the raw body would be compressed!")
        print("But Flask's get_data() reads the COMPRESSED bytes when raw_body = request.get_data()")
        print()

print("=== TEST: Send gzipped body ===")
import gzip
body_plain = json.dumps({"object": "instagram", "entry": []}, ensure_ascii=True, separators=(",", ":")).encode()
body_gzip = gzip.compress(body_plain)

# Meta computes signature on the COMPRESSED body
sig_gzip = "sha256=" + hmac.new(APP_SECRET.encode(), body_gzip, hashlib.sha256).hexdigest()

headers = {
    "Content-Type": "application/json",
    "Content-Encoding": "gzip",
    "X-Hub-Signature-256": sig_gzip
}
resp = requests.post(WEBHOOK_URL, data=body_gzip, headers=headers, timeout=10)
print(f"Gzipped body - Status: {resp.status_code} - {resp.text}")
