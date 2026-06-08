"""Module defining the model for a reservation."""

from django.db import models
from django.db.models import CheckConstraint, F, Q
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from loefsys.members.models.user import User

from .reservable import Reservable


class Reservation(TimeStampedModel):
    """Model describing a reservation of a reservable item.

    A reservation is a 'time-claim' anyone can put on a reservable item. It has a start
    time and end time which is after the start time. The start time may be in the past,
    but only an admin can create reservation that ends in the past. The start time and
    end time may be on different dates, as long as the start time is earlier than the
    end time. A reservation has a reference to a person (or possibly to a group). A
    reservation has a function which can calculate any costs related to that
    reservation. A reservation has a log, which the user must fill in after the
    reservation has ended. A reservation can be linked to a group, training or event.

    A boat reservation can be linked to a training (or event). If it is not then it must
    be reserved by a person with the required skipper's certificate. If the boat has an
    engine, then the user can set an amount of engine-hours used.

    Attributes
    ----------
    reservable : ~loefsys.reservations.models.reservable.Reservable
        The item for which a reservation is made.
    user : ~loefsys.users.models.member.User
        The user making a reservation.
    request : ~loefsys.requests.models.request.Request
        The request for this reservation.
    start : ~datetime.datetime
        The start timestamp of the reservation.
    end : ~datetime.datetime
        The end timestamp of the reservation.
    """

    reservable = models.ForeignKey(
        Reservable,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reservations_set"
    )

    start = models.DateTimeField(verbose_name=_("Start time"))
    end = models.DateTimeField(verbose_name=_("End time"))

    class Meta:
        constraints = (
            CheckConstraint(
                condition=Q(end__gt=F("start")),
                name="end_gt_start",
                violation_error_message="End time cannot be before the start time.",
            ),
        )

    def __str__(self) -> str:
        return f"Reservation {self.reservable} from {self.start} to {self.end} by {self.user}"

    def clean_timeslot(self):
        """Validate the timeslot of the reservation."""
        if (Reservation.objects
                .exclude(pk=self.pk).filter(reservable=self.reservable)
                .filter(start__lt=self.end, end__gt=self.start)  # If both are true, timeslots overlap
                .exists()):
            raise ValidationError("A reservation already exists for the given timeslot.")

    def clean(self):
        """Validate the reservation.

        Raises
        ------
            ValidationError
        """
        # First we validate the timeslot.
        self.clean_timeslot()

        # Then we let the reservable validate the reservation. The reservable can add additional requirements, for
        # example a boat can require an authorized skipper to be set.
        self.reservable.validate_reservation(self)
