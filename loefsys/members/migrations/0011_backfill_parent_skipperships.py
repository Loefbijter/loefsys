"""Give every skipper the lower skipperships their skippership builds on.

Some users were imported with only their highest skippership (e.g. Laser+
without Laser). The skippership hierarchy (``Skippership.parent``) says the
lower ones must be held too, so add any that are missing, dated the same as
the skippership that implies them.
"""

from django.db import migrations


def backfill_parent_skipperships(apps, schema_editor):
    Skippership = apps.get_model("members", "Skippership")
    UserSkippership = apps.get_model("members", "UserSkippership")

    parents = dict(Skippership.objects.values_list("pk", "parent_id"))
    held = {}
    for user_id, skippership_id, since in UserSkippership.objects.values_list(
        "user_id", "skippership_id", "since"
    ):
        held.setdefault(user_id, {})[skippership_id] = since

    missing = []
    for user_id, skipperships in held.items():
        added = {}
        for skippership_id, since in skipperships.items():
            parent = parents.get(skippership_id)
            seen = set()
            while parent is not None and parent not in seen:
                seen.add(parent)
                if parent not in skipperships:
                    earlier = added.get(parent)
                    added[parent] = since if earlier is None else min(earlier, since)
                parent = parents.get(parent)
        missing.extend(
            UserSkippership(user_id=user_id, skippership_id=pk, since=since)
            for pk, since in added.items()
        )
    UserSkippership.objects.bulk_create(missing)


class Migration(migrations.Migration):
    dependencies = [("members", "0010_remove_userskippership_given_by")]

    operations = [
        migrations.RunPython(backfill_parent_skipperships, migrations.RunPython.noop)
    ]
