"""Module defining the user skippership model."""

from collections.abc import Collection
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .skippership import Skippership
from .user import User


class UserSkippership(models.Model):
    """Model connecting a user to a skippership they have obtained.

    Attributes
    ----------
    user : ~loefsys.members.models.user.User
        The user that has obtained the skippership.
    skippership : ~loefsys.members.models.skippership.Skippership
        The skippership that the user has obtained.
    since : ~datetime.date
        The date the skippership was obtained.
    given_by : ~django.db.models.query.QuerySet of ~loefsys.members.models.user.User
        The skippers that have authorized that the user obtained the skippership.
    pending_skippership_ids : ~collections.abc.Collection of int
        Skipperships the user is being given in the same form submission, which
        count as held when checking the required skippership.
    """

    pending_skippership_ids: Collection[int] = frozenset()

    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="user_skipperships"
    )
    skippership = models.ForeignKey(
        to=Skippership, on_delete=models.CASCADE, related_name="user_skipperships"
    )
    since = models.DateField(
        verbose_name=_("Skippership since"),
        help_text=_("The date the user obtained the skippership."),
        default=date.today,
    )
    given_by = models.ManyToManyField(
        User,
        verbose_name=_("Skippers authorized"),
        help_text=_("The skippers that have authorized the skippership."),
        related_name="authorized_skipperships",
        related_query_name="authorized_skipper",
        blank=True,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["user", "skippership"], name="unique_skippership"
            ),
        )

    def __str__(self) -> str:
        return f"{self.skippership.name} {self.user.display_name}"

    def clean(self) -> None:
        """Require the user to hold the skippership's parent skippership."""
        super().clean()
        if self.skippership_id is None:
            return
        required = self.skippership.parent
        if required is None or required.pk in self.pending_skippership_ids:
            return
        if (
            self.user_id is None
            or not UserSkippership.objects.filter(
                user_id=self.user_id, skippership=required
            ).exists()
        ):
            raise ValidationError(
                _("%(skippership)s requires %(required)s first."),
                params={"skippership": self.skippership, "required": required},
            )
