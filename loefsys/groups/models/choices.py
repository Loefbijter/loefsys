"""Module containing enums for choice fields in the models for groups."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class FraternityGenders(models.IntegerChoices):
    """The possible type of the fraternity.

    Fraternities are typically divided into three categories: mainly male,
    mainly female and mixed.
    """

    MIXED = 0, _("Mixed")
    """Used for mixed-gender fraternities."""

    FEMALE = 1, _("Female")
    """Used for mainly female fraternities."""

    MALE = 2, _("Male")
    """Used for mainly male fraternities."""
