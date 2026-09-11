"""Quick script to dump a template user row for inspection."""

import sqlite3

c = sqlite3.connect("db.sqlite")
cur = c.cursor()
cur.execute("PRAGMA table_info('members_user')")
cols = [r[1] for r in cur.fetchall()]
cur.execute("SELECT * FROM members_user WHERE id=1")
row = cur.fetchone()
print("COLUMNS:", cols)
print("ROW:", row)
c.close()
