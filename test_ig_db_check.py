import sqlite3, json

# Check if we have any Instagram messages in the DB
for db_name in ["rcagents.db", "royal_orders.db"]:
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        if c.fetchone():
            # Check what platforms we have
            c.execute("SELECT DISTINCT platform FROM messages")
            platforms = [r[0] for r in c.fetchall()]
            print(f"=== {db_name} - Platforms: {platforms} ===")
            
            for plat in platforms:
                c.execute(f"SELECT COUNT(*) FROM messages WHERE platform=?", (plat,))
                count = c.fetchone()[0]
                print(f"  {plat}: {count} messages")
                
                # Show last 3 messages per platform with sender_id
                c.execute(f"SELECT sender_id, message, reply, timestamp FROM messages WHERE platform=? ORDER BY timestamp DESC LIMIT 3", (plat,))
                for row in c.fetchall():
                    sid = row[0]
                    msg = str(row[1])[:50] if row[1] else "N/A"
                    reply = str(row[2])[:50] if row[2] else "N/A"
                    ts = str(row[3])[:19] if row[3] else "N/A"
                    print(f"    [{ts}] {sid[:30]}: '{msg}' -> '{reply}'")
        
        print()
        conn.close()
    except Exception as e:
        print(f"Error with {db_name}: {e}")
        print()
