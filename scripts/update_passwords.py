"""Update passwords in the local SQLite DB for dev users."""

import os
import sqlite3

import django
from django.contrib.auth.hashers import make_password

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loefsys.settings")

django.setup()

DB = "db.sqlite"
conn = sqlite3.connect(DB)
cur = conn.cursor()

creds = [
    ("member@example.test", "memberpass123"),
    ("eventcreator@example.test", "eventpass123"),
    ("admin@example.test", "adminpass123"),
]

for email, plain in creds:
    hashed = make_password(plain)
    cur.execute("UPDATE members_user SET password=? WHERE email=?", (hashed, email))
    print("Updated password for", email)

conn.commit()
conn.close()
print("Done")
