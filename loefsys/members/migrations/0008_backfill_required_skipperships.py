from django.db import migrations

from loefsys.members.skipperships import backfill_required_skipperships


def backfill(apps, schema_editor):
    backfill_required_skipperships(
        apps.get_model("members", "Skippership"),
        apps.get_model("members", "UserSkippership"),
    )


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0007_add_loefbijter_groups_m2m"),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
