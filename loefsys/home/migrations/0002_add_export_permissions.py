from django.db import migrations


def create_export_permissions(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")

    # list of (app_label, model_name) to create export permissions for
    targets = [
        ("members", "user"),
        ("members", "skippership"),
        ("members", "userskippership"),
        ("groups", "board"),
        ("groups", "committee"),
        ("groups", "fraternity"),
        ("groups", "taskforce"),
        ("groups", "yearclub"),
        ("reservations", "reservabletype"),
        ("reservations", "reservableboat"),
        ("reservations", "reservablematerial"),
        ("reservations", "reservableroom"),
        ("reservations", "boatdamagerecord"),
        ("reservations", "boatlogbook"),
        ("reservations", "reservation"),
        ("events", "event"),
        ("events", "eventregistration"),
        ("events", "registrationformfield"),
        ("home", "announcement"),
        ("home", "staticpage"),
    ]

    for app_label, model in targets:
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            # If the model doesn't exist in this environment, skip
            continue

        codename = f"export_{model}"
        try:
            # Prefer the human-readable model verbose_name when possible
            model_class = ct.model_class()
            if model_class is not None:
                model_label = getattr(model_class._meta, "verbose_name", ct.model)
            else:
                model_label = ct.model
        except Exception:
            model_label = ct.model
        name = f"Can export {model_label}"

        # Create permission if it doesn't already exist
        Permission.objects.get_or_create(content_type=ct, codename=codename, defaults={"name": name})


def remove_export_permissions(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")

    targets = [
        ("members", "user"),
        ("members", "skippership"),
        ("members", "userskippership"),
        ("groups", "board"),
        ("groups", "committee"),
        ("groups", "fraternity"),
        ("groups", "taskforce"),
        ("groups", "yearclub"),
        ("reservations", "reservabletype"),
        ("reservations", "reservableboat"),
        ("reservations", "reservablematerial"),
        ("reservations", "reservableroom"),
        ("reservations", "boatdamagerecord"),
        ("reservations", "boatlogbook"),
        ("reservations", "reservation"),
        ("events", "event"),
        ("events", "eventregistration"),
        ("events", "registrationformfield"),
        ("home", "announcement"),
        ("home", "staticpage"),
    ]

    for app_label, model in targets:
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            continue
        codename = f"export_{model}"
        Permission.objects.filter(content_type=ct, codename=codename).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0001_initial"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(create_export_permissions, remove_export_permissions),
    ]
