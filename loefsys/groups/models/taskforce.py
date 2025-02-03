"""Module containing the model definitions for a taskforce."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .group import LoefbijterGroup


class Taskforce(LoefbijterGroup):
    """Model representing a taskforce.

    A taskforce is a group of people that have a joined task, while not being
    a committee.

    Attributes
    ----------
    requires_nda : bool
        A flag that shows whether an NDA needs to be signed to be in the taskforce.
    """

    requires_nda = models.BooleanField(
        default=False,
        help_text=_(
            "If this is checked an NDA needs to be signed to be part of this taskforce."
        ),
    )
