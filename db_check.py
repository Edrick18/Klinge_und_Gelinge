import sqlite3
db = sqlite3.connect('spiel.sqlite')
c = db.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("Tables:", tables)
for t in tables:
    c.execute(f"PRAGMA table_info({t})")
    cols = c.fetchall()
    print(f"\n{t}:")
    for col in cols:
        print(f"  {col[1]} ({col[2]})")
