"""
Check AI settings for store_id=1 via HTTP (no auth needed for stats)
"""
import urllib.request, json

# Check stats
r = urllib.request.urlopen("https://rcagents.space/api/stats?store_id=1", timeout=10)
data = json.loads(r.read())
print("=== STATS ===")
print(json.dumps(data, indent=2, ensure_ascii=False))

# Also try a direct webhook test to trigger get_or_create_ai_settings
import urllib.request
payload = json.dumps({
    "object": "page",
    "entry": [{
        "id": "1040729219115342",
        "messaging": [{
            "sender": {"id": "check_ai_trigger"},
            "message": {"text": "test ai trigger"}
        }]
    }]
}).encode()
req = urllib.request.Request(
    "https://rcagents.space/webhook", 
    data=payload,
    headers={"Content-Type": "application/json"}
)
r2 = urllib.request.urlopen(req, timeout=10)
print(f"\n=== WEBHOOK TEST ===")
print(f"Status: {r2.status}")
print(f"Response: {r2.read().decode()}")

# Check stats again
r3 = urllib.request.urlopen("https://rcagents.space/api/stats?store_id=1", timeout=10)
data3 = json.loads(r3.read())
print(f"\n=== STATS AFTER WEBHOOK ===")
print(f"ai_configured: {data3.get('ai_configured')}")
print(f"ai_model: {data3.get('ai_model')}")
print(f"messages_today: {data3.get('messages_today')}")
print(f"total_messages: {data3.get('total_messages')}")
