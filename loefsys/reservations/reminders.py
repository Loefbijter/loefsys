"""Module for reminding members to fill in the logbook after a boat reservation."""

import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone, translation

from loefsys.reservations.models.choices import ReservableCategories
from loefsys.reservations.models.reservation import Reservation

logger = logging.getLogger(__name__)

REMINDER_DELAY = timedelta(hours=2)
"""How long after a reservation ends the reminder is sent."""

REMINDER_WINDOW = timedelta(days=7)
"""Reservations that ended longer ago than this are not reminded about.

This matches how long the reservation list keeps showing finished reservations, and
stops a first run from emailing about every old reservation.
"""


def reservations_needing_logbook_reminder(
    now: datetime | None = None,
) -> QuerySet[Reservation]:
    """Return finished boat reservations without a logbook that were not reminded."""
    now = now or timezone.now()
    return (
        Reservation.objects.filter(
            reservable__type__category=ReservableCategories.BOAT,
            end__lte=now - REMINDER_DELAY,
            end__gte=now - REMINDER_WINDOW,
            boat_logbook__isnull=True,
            logbook_reminder_sent_at__isnull=True,
        )
        .exclude(request_status=Reservation.RequestStatus.DENIED)
        .select_related("reservable", "user")
        .order_by("end")
    )


def send_logbook_reminder(reservation: Reservation) -> None:
    """Email the member who made the reservation to fill in its logbook."""
    path = reverse("reservations:boat-logbook", kwargs={"pk": reservation.pk})
    context = {
        "reservation": reservation,
        "user": reservation.user,
        "boat": reservation.reservable.name,
        "logbook_url": f"{settings.SITE_URL.rstrip('/')}{path}",
    }
    # Members get Dutch by default; there is no per-member language preference.
    with translation.override(settings.LANGUAGE_CODE):
        subject = render_to_string(
            "reservations/emails/logbook_reminder_subject.txt", context
        )
        message = render_to_string(
            "reservations/emails/logbook_reminder_body.txt", context
        )
    send_mail(
        f"{settings.EMAIL_SUBJECT_PREFIX} {' '.join(subject.split())}",
        message,
        settings.DEFAULT_FROM_EMAIL,
        [reservation.user.email],
    )


def send_logbook_reminders(now: datetime | None = None) -> int:
    """Send every due logbook reminder and return how many were sent.

    A reservation is only marked as reminded once its email went out, so a failed
    email is retried on the next run.
    """
    sent = 0
    for reservation in reservations_needing_logbook_reminder(now):
        try:
            send_logbook_reminder(reservation)
        except Exception:
            logger.exception(
                "Failed to send logbook reminder for reservation %s", reservation.pk
            )
            continue
        reservation.logbook_reminder_sent_at = timezone.now()
        reservation.save(update_fields=["logbook_reminder_sent_at"])
        sent += 1
    return sent
