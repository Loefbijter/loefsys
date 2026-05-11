"""Module defining the user skippership model."""

from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _

from .skippership import Skippership
from .user import User


class UserSkippership(models.Model):
    """Model connecting a user to a skippership they have obtained.

    Attributes
    ----------
    user : ~loefsys.users.models.user.User
        The user that has obtained the skippership.
    skippership : ~loefsys.users.models.skippership.Skippership
        The skippership that the user has obtained.
    since : ~datetime.date
        The date the skippership was obtained.
    given_by : ~django.db.models.query.QuerySet of ~loefsys.users.models.user.User
        The skippers that have authorized that the user obtained the skippership.
    """

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    skippership = models.ForeignKey(to=Skippership, on_delete=models.CASCADE)
    since = models.DateField(
        verbose_name=_("Skippership since"),
        help_text=_("The date the user obtained the skippership."),
        default=date.today,
    )
    given_by = models.ManyToManyField(
        User,
        verbose_name=_("Skippers authorized"),
        help_text=_("The skippers that have authorized the skippership."),
        related_name="authorized_skippers",
        related_query_name="authorized_skipper",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["user", "skippership"], name="unique_skippership"
            ),
        )

    def __str__(self) -> str:
        return f"{self.skippership.name} {self.user.display_name}"
