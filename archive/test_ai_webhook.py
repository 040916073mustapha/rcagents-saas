"""
Test: Send a simulated webhook message and check if server.py now uses the new AI model
"""
import json, urllib.request

# Simulate a WhatsApp webhook message (this triggers generate_ai_reply)
payload = json.dumps({
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "1212786725251029",
        "changes": [{
            "value": {
                "metadata": {"phone_number_id": "1212786725251029"},
                "messages": [{
                    "from": "could_be_anything",
                    "text": {"body": "Bonjour, est-ce que vous avez des chaussures en taille 38?"}
                }]
            }
        }]
    }]
}).encode()

req = urllib.request.Request(
    "https://rcagents.space/whatsapp/webhook",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    print(f"Status: {resp.status}")
    body = resp.read().decode()
    print(f"Body: {body}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'):
        print(f"Body: {e.read().decode()}")
