from datetime import date

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Skippership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=40, unique=True, verbose_name="Skippership"),
                ),
            ],
            options={"verbose_name": "Skippership", "verbose_name_plural": "Skipperships"},
        ),
        migrations.CreateModel(
            name="UserSkippership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "since",
                    models.DateField(
                        default=date.today,
                        help_text="The date the user obtained the skippership.",
                        verbose_name="Skippership since",
                    ),
                ),
                (
                    "given_by",
                    models.ManyToManyField(
                        blank=True,
                        related_name="authorized_skipperships",
                        related_query_name="authorized_skipper",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Skippers authorized",
                        help_text="The skippers that have authorized the skippership.",
                    ),
                ),
                (
                    "skippership",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="user_skipperships",
                        to="members.Skippership",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="user_skipperships",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=["user", "skippership"],
                        name="unique_skippership",
                    )
                ]
            },
        ),
        migrations.AddField(
            model_name="skippership",
            name="skippers",
            field=models.ManyToManyField(
                through="members.UserSkippership",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Skippers",
                help_text="The skippers that have this skippership.",
                related_name="skipperships",
                related_query_name="skippership",
            ),
        ),
    ]
