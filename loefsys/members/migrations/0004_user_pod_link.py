from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0003_add_profile_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="pod_link",
            field=models.URLField(
                blank=True,
                help_text="Plak hier de link van de POD",
                max_length=512,
                verbose_name="POD link",
            ),
        ),
    ]
