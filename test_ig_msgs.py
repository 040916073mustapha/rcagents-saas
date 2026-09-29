import sqlite3
conn = sqlite3.connect("royal_orders.db")
c = conn.cursor()
c.execute("SELECT DISTINCT platform FROM messages")
platforms = [r[0] for r in c.fetchall()]
print(f"Platforms in messages: {platforms}")
for plat in platforms:
    c.execute("SELECT COUNT(*) FROM messages WHERE platform=?", (plat,))
    count = c.fetchone()[0]
    c.execute("SELECT sender_id, message, reply, created_at FROM messages WHERE platform=? ORDER BY created_at DESC LIMIT 5", (plat,))
    rows = c.fetchall()
    print(f"  {plat}: {count} messages")
    for r in rows:
        sid = str(r[0])[:30] if r[0] else "N/A"
        msg = str(r[1])[:50] if r[1] else "N/A"
        reply = str(r[2])[:50] if r[2] else "N/A"
        ts = str(r[3])[:19] if r[3] else "N/A"
        print(f"    [{ts}] {sid}: '{msg}' -> '{reply}'")
print()
# Check if we have 'instagram' platform
c.execute("SELECT COUNT(*) FROM messages WHERE platform='instagram'")
ig_count = c.fetchone()[0]
print(f"Instagram messages count: {ig_count}")
if ig_count > 0:
    c.execute("SELECT sender_id, message, reply, created_at FROM messages WHERE platform='instagram' ORDER BY created_at DESC")
    for r in c.fetchall():
        print(f"  [{r[3]}] {r[0][:30]}: '{str(r[1])[:50]}' -> '{str(r[2])[:50]}'")
conn.close()
