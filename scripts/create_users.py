"""Script to create convenience users for local/dev environments."""
# ruff: noqa

import os

import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loefsys.settings")

django.setup()

User = get_user_model()


def ensure_user(  # noqa: PLR0913, PLR0917
    email, password, first_name="", last_name="", is_staff=False, is_superuser=False
):
    """Ensure a user with the given details exists and return it."""
    user = User.objects.filter(email=email).first()
    if user:
        print(f"User exists: {email}")
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_active = True
        user.pod_link = ""
        user.set_password(password)
        user.save()
        return user

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=is_staff,
        is_superuser=is_superuser,
        pod_link="",
    )
    print(f"Created user: {email}")
    return user


with transaction.atomic():
    member = ensure_user(
        "member@example.test",
        "memberpass123",
        first_name="Average",
        last_name="Member",
        is_staff=False,
        is_superuser=False,
    )
    event_creator = ensure_user(
        "eventcreator@example.test",
        "eventpass123",
        first_name="Event",
        last_name="Creator",
        is_staff=True,
        is_superuser=False,
    )
    admin = ensure_user(
        "admin@example.test",
        "adminpass123",
        first_name="Site",
        last_name="Admin",
        is_staff=True,
        is_superuser=True,
    )

    # Try to grant add_event permission to event_creator (useful for admin listing)
    try:
        perm = Permission.objects.get(
            codename="add_event", content_type__app_label="events"
        )
        event_creator.user_permissions.add(perm)
        print("Granted events.add_event to eventcreator@example.test")
    except Permission.DoesNotExist:
        print("Permission events.add_event not found; skipping")

    print("\nSummary:")
    print("Member: email=member@example.test password=memberpass123 is_staff=False")
    print(
        "Event creator: email=eventcreator@example.test password=eventpass123 is_staff=True (granted add_event if present)"
    )
    print(
        "Admin: email=admin@example.test password=adminpass123 is_staff=True is_superuser=True"
    )
