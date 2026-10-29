"""Let activity managers add members to the events they manage.

The ``events.add_eventregistration`` permission is what the event admin checks before
showing the form to add members. Which events a manager can do this for is still
decided by the ``events.manage_<category>_events`` permissions.
"""

from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations

ACTIVITY_MANAGERS_GROUP = "Activity managers"

ADDED_PERMISSIONS = ("add_eventregistration",)


def add_registration_permissions(apps, schema_editor):
    # Permissions are normally created after all migrations have run, so create
    # them now to be able to assign them on a fresh database.
    create_permissions(global_apps.get_app_config("events"), apps=apps, verbosity=0)

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    permissions = Permission.objects.filter(
        content_type__app_label="events", codename__in=ADDED_PERMISSIONS
    )
    group, _ = Group.objects.get_or_create(name=ACTIVITY_MANAGERS_GROUP)
    group.permissions.add(*permissions)


def remove_registration_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    permissions = Permission.objects.filter(
        content_type__app_label="events", codename__in=ADDED_PERMISSIONS
    )
    for group in Group.objects.filter(name=ACTIVITY_MANAGERS_GROUP):
        group.permissions.remove(*permissions)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("events", "0007_registration_added_by_organizer"),
    ]

    operations = [
        migrations.RunPython(
            add_registration_permissions, remove_registration_permissions
        ),
    ]
