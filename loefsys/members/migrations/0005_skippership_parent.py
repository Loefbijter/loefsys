from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0004_user_pod_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="skippership",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                help_text="The skippership that must be obtained before this one.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="members.skippership",
                verbose_name="Parent skippership",
            ),
        ),
    ]
