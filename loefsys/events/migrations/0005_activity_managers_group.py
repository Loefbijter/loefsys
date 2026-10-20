"""Create the preset group for activity managers.

The group gets the base permissions to create and manage events. Which categories
its members may manage is decided by the ``events.manage_<category>_events``
permissions, granted to this group or to any other group the user belongs to.

Groups and users that could already change events keep doing so for every
category, so this migration doesn't take access away from anyone.
"""

from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations

ACTIVITY_MANAGERS_GROUP = "Activity managers"

BASE_PERMISSIONS = (
    "add_event",
    "change_event",
    "delete_event",
    "view_event",
    "add_eventorganizer",
    "change_eventorganizer",
    "delete_eventorganizer",
    "view_eventorganizer",
    "add_registrationformfield",
    "change_registrationformfield",
    "delete_registrationformfield",
    "view_registrationformfield",
)

CATEGORY_PERMISSIONS = (
    "manage_other_events",
    "manage_alumni_events",
    "manage_association_events",
    "manage_competition_events",
    "manage_leisure_events",
    "manage_sailing_events",
    "manage_training_events",
)


def create_activity_managers_group(apps, schema_editor):
    # Permissions are normally created after all migrations have run, so create
    # them now to be able to assign them on a fresh database.
    create_permissions(global_apps.get_app_config("events"), apps=apps, verbosity=0)

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    LoefbijterGroup = apps.get_model("groups", "LoefbijterGroup")
    User = apps.get_model("members", "User")

    event_permissions = Permission.objects.filter(content_type__app_label="events")
    base_permissions = event_permissions.filter(codename__in=BASE_PERMISSIONS)
    category_permissions = list(
        event_permissions.filter(codename__in=CATEGORY_PERMISSIONS)
    )
    change_event = event_permissions.get(codename="change_event")

    for model in (Group, LoefbijterGroup):
        for group in model.objects.filter(permissions=change_event):
            group.permissions.add(*category_permissions)
    for user in User.objects.filter(user_permissions=change_event):
        user.user_permissions.add(*category_permissions)

    group, _ = Group.objects.get_or_create(name=ACTIVITY_MANAGERS_GROUP)
    group.permissions.add(*base_permissions)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("groups", "0002_add_groupmembership"),
        ("members", "0001_initial"),
        ("events", "0004_event_category_permissions"),
    ]

    operations = [
        migrations.RunPython(
            create_activity_managers_group, migrations.RunPython.noop
        ),
    ]
