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
    parent : ~loefsys.members.models.skippership.Skippership | None
        The skippership that must be obtained before this one.
    skippers : ~django.db.models.query.QuerySet of UserSkippership
        The users that have obtained the skippership.
    """

    name = models.CharField(max_length=40, verbose_name=_("Skippership"), unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent skippership"),
        help_text=_("The skippership that must be obtained before this one."),
    )
    skippers: models.ManyToManyField = models.ManyToManyField(
        User,
        through="UserSkippership",
        verbose_name=_("Skippers"),
        help_text=_("The skippers that have this skippership."),
        related_name="skipperships",
        related_query_name="skippership",
    )

    class Meta:
        verbose_name = _("Skippership")
        verbose_name_plural = _("Skipperships")

    def __str__(self) -> str:
        return self.name
