import sqlite3
conn = sqlite3.connect("rcagents.db")
c = conn.cursor()

print("=== Channels ===")
c.execute("SELECT channel_type, platform_id, platform_name FROM channels")
for r in c.fetchall():
    print(f"  type={r[0]} pid={str(r[1])[:30]} name={r[2]}")

print()
print("=== Conversations (instagram) ===")
c.execute("SELECT channel, platform_conversation_id, customer_name FROM conversations WHERE channel='instagram'")
for r in c.fetchall():
    print(f"  channel={r[0]} conv_id={str(r[1])[:30]} customer={r[2]}")

print()
actual = c.fetchall()
print(f"IG conversation count: {len(actual)}")

print()
print("=== Messages per channel ===")
c.execute("SELECT channel, COUNT(*) FROM messages GROUP BY channel")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")
conn.close()
