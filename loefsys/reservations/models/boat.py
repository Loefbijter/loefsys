"""Module defining the model for a boat that can be reserved."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .reservable import Reservable


class ReservableBoat(Reservable):
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
    provider : ~loefsys.reservations.models.boat.ReservableBoat.Provider
        The provider of the boat.
    requires_skippership : str | None
        The skippership required to reserve this boat.
    """

    class Provider(models.IntegerChoices):
        """Describes the provider of the boat."""

        OTHER = (0, _("Other"))
        """Used for boats available from other providers."""

        LOEFBIJTER = (1, _("Loefbijter"))
        """Used for boats from Loefbijter."""

        CEULEMANS = (2, _("Ceulemans"))
        """Used for boats from Ceulemans."""

    class RequiredSkippership(models.TextChoices):
        """The skippership that is required to use this boat."""

        KB1 = ("KB1", _("KB1"))
        KB2 = ("KB2", _("KB2"))
        KB3 = ("KB3", _("KB3"))
        PICO = ("Pico", _("Pico"))

    capacity = models.PositiveSmallIntegerField(verbose_name=_("Capacity"))
    has_engine = models.BooleanField(
        default=False, verbose_name=_("Boat has an engine")
    )
    provider = models.PositiveSmallIntegerField(
        choices=Provider, default=Provider.OTHER, verbose_name=_("Boat provider")
    )
    requires_skippership = models.CharField(
        max_length=10,
        choices=RequiredSkippership.choices,
        blank=True,
       null=True,
       verbose_name=_("Required skippership"),
       help_text=_("The skippership required to use this boat."),
    )
