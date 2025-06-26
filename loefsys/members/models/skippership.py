"""Module defining the skippership model."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .user import User


class Skippership(models.Model):
    """Model defining skipperships.

    Attributes
    ----------
    name : str
        The name of the skippership.
    skippers : ~django.db.models.query.QuerySet of \
        ~loefsys.users.models.user_skippership.UserSkippership
        The users that have obtained the skippership.
    """

    name = models.CharField(max_length=40, verbose_name=_("Skippership"), unique=True)
    skippers = models.ManyToManyField(
        User,
        through="UserSkippership",
        verbose_name=_("Skippers"),
        help_text=_("The skippers that have this skippership."),
        related_name="skippers",
        related_query_name="skipper",
    )

    def __str__(self) -> str:
        return self.name
