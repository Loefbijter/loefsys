from django.db import migrations, models
from django.db.models import F


def fill_missing_deadlines(apps, schema_editor):
    """Close registration at the start of events that have no deadline."""
    event_model = apps.get_model("events", "Event")
    missing = event_model.objects.filter(registration_deadline__isnull=True)
    # Registration has to open before it closes; drop an opening time that doesn't.
    missing.filter(registration_start__gte=F("start")).update(registration_start=None)
    missing.update(registration_deadline=F("start"))


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0009_organizer_help_texts"),
    ]

    operations = [
        # A deadline at the start itself must be allowed for the filled-in events.
        migrations.RemoveConstraint(model_name="event", name="event_start_gt_reg_end"),
        migrations.AddConstraint(
            model_name="event",
            constraint=models.CheckConstraint(
                condition=models.Q(("start__gte", models.F("registration_deadline"))),
                name="event_start_gte_reg_end",
                violation_error_message="registration deadline can't be after start.",
            ),
        ),
        migrations.RunPython(fill_missing_deadlines, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="event",
            name="registration_deadline",
            field=models.DateTimeField(verbose_name="Registration deadline"),
        ),
    ]
