"""Module defining the model for logs."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from loefsys.reservations.models.reservable import ReservableType


class Log(models.Model):
    """Describes a log associated for a boat type.

    Attributes
    ----------
    name : str
        The name of the log.
    boat_type : ~loefsys.reservations.models.reservable.ReservableType
        The type of boat.
    """

    name = models.CharField(max_length=20)
    boat_type = models.ForeignKey(
        ReservableType, on_delete=models.CASCADE, limit_choices_to={"category": "1"}
    )

    def __str__(self):
        return self.name


class Question(models.Model):
    """Describes questions associated with a log.

    Attributes
    ----------
    log: ~loefsys.reservations.models.log.Log
        The associated log.

    """

    log = models.ForeignKey(Log, on_delete=models.CASCADE)

    BOOLEAN_FIELD = "boolean"
    INTEGER_FIELD = "integer"
    TEXT_FIELD = "text"
    DATETIME_FIELD = "datetime"

    FIELD_TYPES = (
        (BOOLEAN_FIELD, _("Boolean")),
        (INTEGER_FIELD, _("Integer")),
        (TEXT_FIELD, _("Text")),
        (DATETIME_FIELD, _("Datetime")),
    )

    type = models.CharField(
        max_length=20, choices=FIELD_TYPES, default=TEXT_FIELD, verbose_name=_("Type")
    )
    subject = models.CharField(max_length=200, verbose_name=_("Subject"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    required = models.BooleanField(default=True, verbose_name=_("Required"))

    def __str__(self):
        return self.subject
