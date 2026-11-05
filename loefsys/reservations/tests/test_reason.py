"""Tests for the reason of a reservation and the skipper in the admin."""

import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from loefsys.members.models import User
from loefsys.reservations.models import Reservable, ReservableType, Reservation
from loefsys.reservations.models.choices import Locations, ReservableCategories


class ReservationReasonTestCase(TestCase):
    member: User
    skipper: User
    admin: User
    room: Reservable

    @classmethod
    def setUpTestData(cls):
        cls.member = User.objects.create_user(
            email="member@example.com",
            password="secure-password",
            first_name="Maaike",
            last_name="Member",
        )
        cls.skipper = User.objects.create_user(
            email="skipper@example.com",
            password="secure-password",
            first_name="Sven",
            last_name="Schipper",
        )
        cls.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="secure-password",
            first_name="Ada",
            last_name="Admin",
        )
        room_type = ReservableType.objects.create(
            name="Room", category=ReservableCategories.ROOM, description="A room"
        )
        cls.room = Reservable.objects.create(
            name="Bestuurskamer",
            description="",
            type=room_type,
            location=Locations.BOARDROOM,
        )

    def post_reservation(self, **extra):
        start = (timezone.localtime() + datetime.timedelta(days=2)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        self.client.force_login(self.member)
        return self.client.post(
            reverse("reservations:reservation-add", args=[Locations.BOARDROOM]),
            {
                "reservable": self.room.pk,
                "start": start.strftime("%Y-%m-%dT%H:%M"),
                "end": (start + datetime.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
                **extra,
            },
        )

    def test_reservation_stores_the_reason(self):
        response = self.post_reservation(reason="Vergadering van de kascommissie.")

        self.assertEqual(response.status_code, 302)
        reservation = Reservation.objects.get(user=self.member)
        self.assertEqual(reservation.reason, "Vergadering van de kascommissie.")

    def test_reason_is_required(self):
        response = self.post_reservation(reason="  ")

        self.assertEqual(response.status_code, 200)
        self.assertIn("reason", response.context["form"].errors)
        self.assertFalse(Reservation.objects.exists())

    def test_admin_list_shows_skipper_and_reason(self):
        start = timezone.now() + datetime.timedelta(days=2)
        Reservation.objects.create(
            reservable=self.room,
            user=self.member,
            authorized_userskippership=self.skipper,
            start=start,
            end=start + datetime.timedelta(hours=2),
            reason="Vergadering van de kascommissie.",
        )
        self.client.force_login(self.admin)

        response = self.client.get(reverse("admin:reservations_reservation_changelist"))

        self.assertContains(response, "Sven Schipper")
        self.assertContains(response, "Vergadering van de kascommissie.")
