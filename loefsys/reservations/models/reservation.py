"""Module defining the model for a reservation."""

from django.db import models
from django.db.models import CheckConstraint, F, Q
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from loefsys.members.models.user import User

# from loefsys.members.models.user_skippership import UserSkippership
from loefsys.reservations.models.boat import Boat
from loefsys.reservations.models.choices import ReservableCategories, ReservationStatus


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
    start : ~datetime.datetime
        The start timestamp of the reservation.
    end : ~datetime.datetime
        The end timestamp of the reservation.
    request_status : ~loefsys.reservations.models.reservation.ReservationStatus
        The status of the reservation.
    request_response : str
        A string containing clarification of the acceptance/decline of the request.
    """

    class RequestStatus(models.IntegerChoices):
        PENDING = 0, _("Pending")
        APPROVED = 1, _("Approved")
        DENIED = 2, _("Denied")

    reservable = models.ForeignKey(Reservable, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reservations_set"
    )

    start = models.DateTimeField(verbose_name=_("Start time"))
    end = models.DateTimeField(verbose_name=_("End time"))
    date_of_creation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
        verbose_name=_("Status"),
    )
    denial_reason = models.TextField(blank=True, verbose_name=_("Denial reason"))

    class Meta:
        constraints = (
            CheckConstraint(
                condition=Q(end__gt=F("start")),
                name="end_gt_start",
                violation_error_message=_("End time cannot be before the start time."),
            ),
        )

    def __str__(self) -> str:
        return (
            f"Reservation {self.reservable} "
            f"from {self.start} to {self.end} by {self.user}"
        )

    def clean_timeslot(self):
        """Validate the timeslot of the reservation."""
        if (
            Reservation.objects.exclude(pk=self.pk)
            .filter(reservable=self.reservable)
            .filter(request_status=self.RequestStatus.APPROVED)
            # If other.start < self.end and other.end > self.start, then it overlaps
            .filter(start__lt=self.end, end__gt=self.start)
            .exists()
        ):
            raise ValidationError(_("A reservation already exists for this timeslot."))

    def clean(self):
        """Validate the reservation.

        Raises
        ------
            ValidationError: This item has already been reserved during this timeslot.
            ValidationError: This item is not reservable at the moment.
            ValidationError: The boat selected requires an authorized skipper to be set.
            ValidationError: The skipper set is not authorized for this boat.
        """
        if not self.reserved_item_id or self.start is None or self.end is None:
            return

        has_overlapping_reservation = Reservation.objects.filter(
            ~Q(pk=self.pk)
            & Q(reserved_item=self.reserved_item)
            & (
                Q(start__range=(self.start, self.end))
                | Q(end__range=(self.start, self.end))
                | Q(start__lt=self.start, end__gt=self.end)
            )
        ).exists()
        if has_overlapping_reservation:
            raise ValidationError(
                "This item has already been reserved during this timeslot."
            )

        if not self.reserved_item.is_reservable:
            raise ValidationError("This item is not reservable at the moment.")

        if self.reserved_item.reservable_type.category == ReservableCategories.BOAT:
            try:
                requires_skippership = Boat.objects.get(
                    pk=self.reserved_item.pk
                ).requires_skippership
            except Boat.DoesNotExist:
                requires_skippership = False

            if requires_skippership:
                # if not self.authorized_userskippership:
                #     raise ValidationError(
                #         "The boat selected requires an authorized skipper to be set."  # noqa: E501
                #     )

                # if (
                #     requires_skippership
                #     != self.authorized_userskippership.skippership
                # ):
                #     raise ValidationError(
                #         "The skipper set is not authorized for this boat."
                #     )
                raise NameError("Skipperships are currently disabled.")

        if self.status == ReservationStatus.DENIED and not self.denial_reason.strip():
            raise ValidationError(
                {
                    "denial_reason": "A denial reason is required when denying a reservation."
                }
            )

        return
