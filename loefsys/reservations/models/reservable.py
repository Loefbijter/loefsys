"""Module defining models for reservable items."""

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

if TYPE_CHECKING:
    from . import Reservation


class ReservableType(TimeStampedModel):
    """Model representing a type of reservable.

    This model exists to be able to make a collection of all reservables of the same
    type. Examples are wetsuits of the same size or the two 'valkjes' Scylla and
    Charybdis.

    Attributes
    ----------
    name : str
        The name of the type.
    category : ~loefsys.reservations.models.choices.ReservableCategories
        The category that the type falls under.
    description : str
        An additional description of the type.
    """

    class Category(models.IntegerChoices):
        """The various categories that reservables are part of."""

        OTHER = (0, _("Other"))
        """Used for types that do not fall under the other categories."""

        BOAT = (1, _("Boat"))
        """Used for boat types."""

        ROOM = (2, _("Room"))
        """Used for room types."""

        MATERIAL = (3, _("Material"))
        """Used for material types."""

    name = models.CharField(max_length=40, verbose_name=_("Material type"), unique=True)
    category = models.PositiveSmallIntegerField(
        choices=Category,
        default=Category.OTHER,
        verbose_name=_("Reservable category"),
    )
    description = models.TextField(verbose_name=_("Type description"))

    def __str__(self) -> str:
        return self.name


class Reservable(TimeStampedModel):
    """The base model for a reservable item.

    A reservable item is an object that can be reserved. It can be set as
    non-reservable, for example due to maintenance. Additionally, it has a location and
    later known complications will be added. TODO add complications.

    Attributes
    ----------
    name : str
        The name of the item.
    description : str
        A description of the item.
    location : ~loefsys.reservations.models.choices.Locations
        The location of the item.
    is_reservable : bool
        Flag to show availability.

        For example, if an item is unavailable due to maintenance, the value is set to
        `False`.
    """

    class Location(models.IntegerChoices):
        """Locations where a reservable can be retrieved."""

        OTHER = (0, _("Other"))
        """Used when the other locations aren't applicable."""

        BOARDROOM = (1, _("Boardroom"))
        """Used when an item is located in the boardroom."""

        BASTION = (2, _("Bastion"))
        """Used when an item is located at the Bastion."""

        KRAAIJ = (3, _("Kraaijenbergse Plassen"))
        """Used when an item is located at the Kraaijenbergse Plassen."""

    name = models.CharField(
        max_length=40,
        verbose_name=_("Name")
    )
    description = models.TextField(
        verbose_name=_("Description")
    )
    type = models.ForeignKey(
        ReservableType,
        on_delete=models.CASCADE,
    )
    location = models.PositiveSmallIntegerField(
        choices=Location,
        default=Location.OTHER,
        verbose_name=_("Location")
    )
    is_reservable = models.BooleanField(
        default=True,
        verbose_name=_("Reservable"),
        help_text=_(
            "When an item is unavailable for reservation, due to maintenance for "
            "example, set this to false."
        ),
    )

    def __str__(self):
        return self.name

    def validate_reservation(self, reservation: "Reservation") -> None:
        """Check if this item can be reserved.

        Checks if the item can be reserved. Subclasses of the ReservableItem class can override this and add additional requirements.

        Parameters
        ----------
        reservation : ~loefsys.reservations.models.reservable.Reservation
            The reservation that is attempted to be done.

        Raises
        ------
            ValidationError
        """
        if not self.is_reservable:
            raise ValidationError(_("This item cannot be reserved."))
