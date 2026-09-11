"""Small helper to inspect members_user table columns for debugging."""

import sqlite3

conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()
cur.execute("PRAGMA table_info('members_user')")
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()
