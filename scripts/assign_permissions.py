"""Assign a few convenience permissions and flags for local/dev usage."""

import os

import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loefsys.settings")

django.setup()

User = get_user_model()

try:
    u = User.objects.get(email="eventcreator@example.test")
    perm = Permission.objects.get(
        codename="add_event", content_type__app_label="events"
    )
    u.user_permissions.add(perm)
    print("Granted events.add_event to eventcreator@example.test")
except Exception as e:
    print("Could not grant permission or find user:", e)

# Ensure admin user has is_staff and is_superuser set via ORM update.
try:
    admin = User.objects.get(email="admin@example.test")
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print("Ensured admin flags set")
except Exception as e:
    print("Admin ensure failed:", e)

print("Done")
