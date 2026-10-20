"""Replace the staff flag with the "Admin" permission.

Admin access now follows from a user's permissions. Every user who had the staff
flag gets the new ``members.access_admin`` ("Admin") permission so they keep
their access, after which the flag is removed.
"""

from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations


def get_admin_permission(apps):
    # Permissions are normally created after all migrations have run.
    create_permissions(global_apps.get_app_config("members"), apps=apps, verbosity=0)
    Permission = apps.get_model("auth", "Permission")
    return Permission.objects.get(
        codename="access_admin", content_type__app_label="members"
    )


def staff_to_admin_permission(apps, schema_editor):
    User = apps.get_model("members", "User")
    permission = get_admin_permission(apps)
    for user in User.objects.filter(is_staff=True):
        user.user_permissions.add(permission)


def admin_permission_to_staff(apps, schema_editor):
    User = apps.get_model("members", "User")
    permission = get_admin_permission(apps)
    User.objects.filter(user_permissions=permission).update(is_staff=True)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("members", "0007_add_loefbijter_groups_m2m"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "ordering": ("modified",),
                "permissions": (("access_admin", "Admin"),),
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
        ),
        migrations.RunPython(staff_to_admin_permission, admin_permission_to_staff),
        migrations.RemoveField(
            model_name="user",
            name="is_staff",
        ),
    ]
