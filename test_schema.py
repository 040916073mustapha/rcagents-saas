import sqlite3
conn = sqlite3.connect("royal_orders.db")
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for r in c.fetchall():
    print(r[0])
    print("---")
conn.close()
