"""Module containing the model definition for a year club."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .group import LoefbijterGroup


class YearClub(LoefbijterGroup):
    """A year club consists of a group people belonging to the same year.

    A year club is a group of members that joined the association in the same year.
    Year clubs usually host certain events for the association, and are tied to the
    year they joined the association.

    Attributes
    ----------
    year : int
        The year of the year club.
    """

    year = models.PositiveIntegerField(verbose_name=_("Year"))
