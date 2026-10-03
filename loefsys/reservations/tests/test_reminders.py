import datetime
from io import StringIO

from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from loefsys.members.models import User
from loefsys.reservations.models import (
    BoatLogbook,
    ReservableBoat,
    ReservableMaterial,
    ReservableType,
    Reservation,
)
from loefsys.reservations.models.choices import Locations, ReservableCategories
from loefsys.reservations.reminders import send_logbook_reminders
from loefsys.reservations.tasks import send_logbook_reminders as reminder_task


class BrokenBackend(BaseEmailBackend):
    def send_messages(self, _email_messages):
        raise ConnectionError("SMTP server is down")


@override_settings(SITE_URL="https://example.org")
class LogbookReminderTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.user = User.objects.create_user(
            email="sailor@example.com",
            password="secure-password",
            first_name="Sanne",
            last_name="Zeiler",
        )
        boat_type = ReservableType.objects.create(
            name="Boat", category=ReservableCategories.BOAT, description="A boat type"
        )
        self.boat = ReservableBoat.objects.create(
            name="Valk 3",
            description="A boat",
            type=boat_type,
            location=Locations.KRAAIJ,
            is_reservable=True,
            capacity=3,
            has_engine=False,
            provider=ReservableBoat.Provider.LOEFBIJTER,
            requires_skippership=None,
        )

    def reserve(self, *, ended_ago, reservable=None, **kwargs):
        end = self.now - ended_ago
        return Reservation.objects.create(
            reservable=reservable or self.boat,
            user=self.user,
            start=end - datetime.timedelta(hours=4),
            end=end,
            request_status=kwargs.pop(
                "request_status", Reservation.RequestStatus.APPROVED
            ),
            **kwargs,
        )

    def test_reminds_about_a_finished_boat_reservation_without_logbook(self):
        reservation = self.reserve(ended_ago=datetime.timedelta(hours=3))

        self.assertEqual(send_logbook_reminders(self.now), 1)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["sailor@example.com"])
        self.assertIn("Valk 3", email.subject)
        self.assertIn("Sanne", email.body)
        path = reverse("reservations:boat-logbook", kwargs={"pk": reservation.pk})
        self.assertIn(f"https://example.org{path}", email.body)
        reservation.refresh_from_db()
        self.assertIsNotNone(reservation.logbook_reminder_sent_at)

    def test_email_is_in_dutch(self):
        self.reserve(ended_ago=datetime.timedelta(hours=3))

        send_logbook_reminders(self.now)

        self.assertIn("logboek", mail.outbox[0].subject.lower())

    def test_reminds_only_once(self):
        self.reserve(ended_ago=datetime.timedelta(hours=3))

        send_logbook_reminders(self.now)
        self.assertEqual(send_logbook_reminders(self.now), 0)

        self.assertEqual(len(mail.outbox), 1)

    def test_skips_reservations_that_do_not_need_a_reminder(self):
        filled = self.reserve(ended_ago=datetime.timedelta(hours=3))
        BoatLogbook.objects.create(reservation=filled, wind_force=3, motor_hours=0)
        self.reserve(ended_ago=datetime.timedelta(minutes=30))
        self.reserve(ended_ago=-datetime.timedelta(hours=2))
        self.reserve(ended_ago=datetime.timedelta(days=8))
        self.reserve(
            ended_ago=datetime.timedelta(hours=3),
            request_status=Reservation.RequestStatus.DENIED,
        )
        material = ReservableMaterial.objects.create(
            name="Wetsuit",
            description="A wetsuit",
            type=ReservableType.objects.create(
                name="Gear", category=ReservableCategories.OTHER, description="Gear"
            ),
            location=Locations.KRAAIJ,
            is_reservable=True,
            size="M",
        )
        self.reserve(ended_ago=datetime.timedelta(hours=3), reservable=material)

        self.assertEqual(send_logbook_reminders(self.now), 0)
        self.assertEqual(mail.outbox, [])

    def test_retries_when_the_email_fails(self):
        reservation = self.reserve(ended_ago=datetime.timedelta(hours=3))

        with (
            override_settings(EMAIL_BACKEND=f"{__name__}.BrokenBackend"),
            self.assertLogs("loefsys.reservations.reminders", "ERROR"),
        ):
            self.assertEqual(send_logbook_reminders(self.now), 0)

        reservation.refresh_from_db()
        self.assertIsNone(reservation.logbook_reminder_sent_at)
        self.assertEqual(send_logbook_reminders(self.now), 1)

    def test_task_and_command_send_reminders(self):
        self.reserve(ended_ago=datetime.timedelta(hours=3))
        self.assertEqual(reminder_task(), 1)

        self.reserve(ended_ago=datetime.timedelta(hours=5))
        out = StringIO()
        call_command("send_logbook_reminders", stdout=out)

        self.assertIn("Sent 1", out.getvalue())
        self.assertEqual(len(mail.outbox), 2)
