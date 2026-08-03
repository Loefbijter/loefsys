"""Module defining boat logbook models."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class BoatDamageRecord(TimeStampedModel):
    """Represents a damage record attached to a boat."""

    boat = models.ForeignKey(
        "reservations.ReservableBoat",
        on_delete=models.CASCADE,
        related_name="damage_records",
        verbose_name=_("Boat"),
    )
    description = models.TextField(verbose_name=_("Damage description"))

    def __str__(self) -> str:
        return self.description


class BoatLogbook(TimeStampedModel):
    """Represents the post-reservation logbook for a boat."""

    reservation = models.OneToOneField(
        "reservations.Reservation",
        on_delete=models.CASCADE,
        related_name="boat_logbook",
        verbose_name=_("Reservation"),
    )
    wind_force = models.PositiveSmallIntegerField(verbose_name=_("Wind force (Bft)"))
    motor_hours = models.PositiveIntegerField(verbose_name=_("Motor hours"))
    refueled = models.BooleanField(
        default=False, verbose_name=_("Did you refuel the boat?")
    )
    has_new_damage = models.BooleanField(
        default=False, verbose_name=_("Did you discover new damage?")
    )
    new_damage_description = models.TextField(
        blank=True, verbose_name=_("New damage description")
    )
    photo = models.ImageField(
        upload_to="reservations/boat-logbooks/",
        blank=True,
        null=True,
        verbose_name=_("Photo of the boat"),
    )

    def __str__(self) -> str:
        return f"Logbook for {self.reservation}"

    def clean(self) -> None:
        """Ensure a damage description is supplied when new damage is reported."""
        if self.has_new_damage and not self.new_damage_description.strip():
            raise ValidationError(
                {
                    "new_damage_description": _(
                        "A damage description is required when new damage was found."
                    )
                }
            )
