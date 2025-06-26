"""Module defining the model for a boat that can be reserved."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from loefsys.members.models.skippership import Skippership

from .choices import FleetChoices
from .reservable import ReservableItem


class Boat(ReservableItem):
    """Describes a boat that can be reserved.

    A boat is part of our or any external fleet of boats. It can be any type of boat.
    A boat requires a certain skipper's certificate. It has a limited capacity and can
    possibly have an engine.

    Attributes
    ----------
    capacity : int
        The capacity of the boat.
    has_engine : bool
        Flag that determines whether the boat has an engine.
    fleet : ~loefsys.reservations.models.choices.FleetChoices
        The provider of the boat.
    requires_skippership : ~loefsys.users.models.skippership.Skippership
        The skippership needed to reserve the boat. Can be none.
    """

    capacity = models.PositiveSmallIntegerField(verbose_name=_("Capacity"))
    has_engine = models.BooleanField(
        default=False, verbose_name=_("Boat has an engine")
    )
    fleet = models.PositiveSmallIntegerField(
        choices=FleetChoices,
        default=FleetChoices.OTHER,
        verbose_name=_("Boat provider"),
    )
    requires_skippership = models.ForeignKey(
        Skippership, null=True, blank=True, on_delete=models.CASCADE
    )
