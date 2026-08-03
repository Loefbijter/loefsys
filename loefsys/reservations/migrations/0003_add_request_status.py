from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='request_status',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='status',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
