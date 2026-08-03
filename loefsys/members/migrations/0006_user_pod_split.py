from django.db import migrations, models


def copy_pod_link_to_kb(apps, schema_editor):
    User = apps.get_model("members", "User")
    for user in User.objects.all():
        # copy existing pod_link into pod_kb_link if present
        val = getattr(user, "pod_link", None)
        if val:
            setattr(user, "pod_kb_link", val)
            user.save(update_fields=["pod_kb_link"])


def noop_reverse(apps, schema_editor):
    # reverse migration: don't try to reconstruct pod_link
    return


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0005_skippership_parent"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="pod_kb_link",
            field=models.URLField(
                blank=True,
                max_length=512,
                verbose_name="KB POD link",
                help_text="Paste the link to your KB POD (Google Sheets) so it can be edited.",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="pod_zb_link",
            field=models.URLField(
                blank=True,
                max_length=512,
                verbose_name="ZB POD link",
                help_text="Paste the link to your ZB POD (Google Sheets) so it can be edited.",
            ),
        ),
        migrations.RunPython(copy_pod_link_to_kb, reverse_code=noop_reverse),
        migrations.RemoveField(model_name="user", name="pod_link"),
    ]
