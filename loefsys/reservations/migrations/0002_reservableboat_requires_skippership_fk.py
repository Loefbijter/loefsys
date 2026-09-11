from django.db import migrations, models
import django.db.models.deletion


def copy_requires_skipperships(apps, schema_editor):
    Skippership = apps.get_model("members", "Skippership")
    ReservableBoat = apps.get_model("reservations", "ReservableBoat")

    for boat in ReservableBoat.objects.all():
        required = getattr(boat, "requires_skippership", "")
        if not required:
            continue

        skippership, _ = Skippership.objects.get_or_create(name=required)
        boat.requires_skippership_new_id = skippership.pk
        boat.save(update_fields=["requires_skippership_new"])


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0006_user_pod_split"),
        ("reservations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservableboat",
            name="requires_skippership_new",
            field=models.ForeignKey(
                blank=True,
                help_text="The skippership required to use this boat.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="required_boats",
                to="members.skippership",
                verbose_name="Required skippership",
            ),
        ),
        migrations.RunPython(copy_requires_skipperships, migrations.RunPython.noop),
        migrations.RemoveField(model_name="reservableboat", name="requires_skippership"),
        migrations.RenameField(
            model_name="reservableboat",
            old_name="requires_skippership_new",
            new_name="requires_skippership",
        ),
    ]
