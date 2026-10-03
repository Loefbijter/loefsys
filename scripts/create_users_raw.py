"""Raw user-creation helper for low-level SQLite inserts used in dev setups."""

import random
import sqlite3
import string
from datetime import datetime

DB = "db.sqlite"


def rand_slug(n=8):
    """Return a short random slug of letters and digits.

    Used for generating unique slugs when inserting raw users.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


conn = sqlite3.connect(DB)
cur = conn.cursor()
# Get schema columns order
cur.execute("PRAGMA table_info('members_user')")
cols = [r[1] for r in cur.fetchall()]
print("columns:", cols)

# Use row id 1 as template
cur.execute("SELECT * FROM members_user WHERE id=1")
template = cur.fetchone()
if not template:
    raise SystemExit("No template user found")

# Map template values
templ_map = dict(zip(cols, template))

now = datetime.utcnow().isoformat(sep=" ")

users_to_create = [
    {
        "email": "member@example.test",
        "password_hash": templ_map[
            "password"
        ],  # reuse template hash (not ideal but works)
        "is_staff": 0,
        "is_superuser": 0,
        "first_name": "Average",
        "last_name": "Member",
    },
    {
        "email": "eventcreator@example.test",
        "password_hash": templ_map["password"],
        "is_staff": 1,
        "is_superuser": 0,
        "first_name": "Event",
        "last_name": "Creator",
    },
    {
        "email": "admin@example.test",
        "password_hash": templ_map["password"],
        "is_staff": 1,
        "is_superuser": 1,
        "first_name": "Site",
        "last_name": "Admin",
    },
]

insert_cols = [c for c in cols if c != "id"]
placeholders = ",".join("?" for _ in insert_cols)

for u in users_to_create:
    row = [None] * len(insert_cols)
    for i, col in enumerate(insert_cols):
        if col == "password":
            row[i] = u["password_hash"]
        elif col == "last_login":
            row[i] = None
        elif col == "is_superuser":
            row[i] = u["is_superuser"]
        elif col == "created":
            row[i] = now
        elif col == "modified":
            row[i] = now
        elif col == "email":
            row[i] = u["email"]
        elif col == "slug":
            row[i] = rand_slug()
        elif col == "is_staff":
            row[i] = u["is_staff"]
        elif col == "is_active":
            row[i] = 1
        elif col == "first_name":
            row[i] = u.get("first_name", templ_map.get("first_name"))
        elif col == "last_name":
            row[i] = u.get("last_name", templ_map.get("last_name"))
        elif col == "initials":
            row[i] = templ_map.get("initials") or ""
        elif col == "nickname":
            row[i] = templ_map.get("nickname") or ""
        elif col == "display_name_preference":
            row[i] = templ_map.get("display_name_preference") or 0
        elif col == "picture":
            row[i] = templ_map.get("picture")
        elif col == "gender":
            row[i] = templ_map.get("gender") or 0
        elif col == "birthday":
            row[i] = templ_map.get("birthday")
        elif col == "show_birthday":
            row[i] = templ_map.get("show_birthday") or 0
        elif col == "phone_number":
            row[i] = templ_map.get("phone_number") or ""
        elif col == "note":
            row[i] = templ_map.get("note") or ""
        elif col == "address_id":
            row[i] = templ_map.get("address_id")
        elif col == "lichting":
            row[i] = templ_map.get("lichting") or ""
        elif col == "title":
            row[i] = templ_map.get("title") or ""
        elif col == "pod_link":
            row[i] = templ_map.get("pod_link") or ""
        elif col == "pod_kb_link":
            row[i] = templ_map.get("pod_kb_link") or ""
        elif col == "pod_zb_link":
            row[i] = templ_map.get("pod_zb_link") or ""
        else:
            # fallback to template
            row[i] = templ_map.get(col)
    try:
        cols_str = ",".join(insert_cols)
        query = f"INSERT INTO members_user ({cols_str}) VALUES ({placeholders})"
        cur.execute(query, row)
        print("Inserted", u["email"])
    except Exception as e:
        print("Failed to insert", u["email"], e)

conn.commit()
conn.close()
print("Done raw inserts")
