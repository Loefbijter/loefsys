"""Module containing the model definitions for a board."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .group import LoefbijterGroup


class Board(LoefbijterGroup):
    """A group model for the board of Loefbijter.

    The board is a group of people that run the association. The board members
    change yearly so every board has a year attached to it.

    Attributes
    ----------
    year : int
        The year of the board, starting in the founding year.
    """

    year = models.PositiveIntegerField(verbose_name=_("Year"))
