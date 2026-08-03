import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from loefsys.members.models import User
from loefsys.reservations.models import (
    BoatDamageRecord,
    BoatLogbook,
    ReservableBoat,
    ReservableType,
    Reservation,
)
from loefsys.reservations.models.choices import Locations, ReservableCategories


class BoatLogbookViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="logbook@example.com",
            password="secure-password",
            first_name="Log",
            last_name="Book",
        )
        self.boat_type = ReservableType.objects.create(
            name="Boat", category=ReservableCategories.BOAT, description="A boat type"
        )
        self.boat = ReservableBoat.objects.create(
            name="Test boat",
            description="A boat",
            type=self.boat_type,
            location=Locations.KRAAIJ,
            is_reservable=True,
            capacity=4,
            has_engine=True,
            provider=ReservableBoat.Provider.LOEFBIJTER,
            requires_skippership="",
        )
        self.reservation = Reservation.objects.create(
            reservable=self.boat,
            user=self.user,
            start=timezone.now() - datetime.timedelta(hours=1),
            end=timezone.now() + datetime.timedelta(hours=2),
            request_status=Reservation.RequestStatus.APPROVED,
        )
        self.existing_damage = BoatDamageRecord.objects.create(
            boat=self.boat, description="Een kras op de romp."
        )

    def test_logbook_form_renders_existing_damage_records(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("reservations:boat-logbook", kwargs={"pk": self.reservation.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.existing_damage.description)
        self.assertContains(response, "Wat was de windkracht")

    def test_past_boat_reservation_without_logbook_stays_visible(self):
        self.client.force_login(self.user)

        past_reservation = Reservation.objects.create(
            reservable=self.boat,
            user=self.user,
            start=timezone.now() - datetime.timedelta(days=2),
            end=timezone.now() - datetime.timedelta(days=1),
            request_status=Reservation.RequestStatus.APPROVED,
        )

        response = self.client.get(reverse("reservations:reservations"))

        self.assertContains(response, past_reservation.reservable.name)

    def test_logbook_can_be_submitted_with_new_damage(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("reservations:boat-logbook", kwargs={"pk": self.reservation.pk}),
            {
                "wind_force": 4,
                "motor_hours": 18,
                "refueled": "on",
                "has_new_damage": "on",
                "new_damage_description": "Een nieuwe deuk in de boeg.",
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "reservations:reservation-detail", kwargs={"pk": self.reservation.pk}
            ),
        )

        logbook = BoatLogbook.objects.get(reservation=self.reservation)
        self.assertEqual(logbook.wind_force, 4)
        self.assertEqual(logbook.motor_hours, 18)
        self.assertTrue(logbook.refueled)
        self.assertTrue(logbook.has_new_damage)
        self.assertTrue(
            BoatDamageRecord.objects.filter(
                boat=self.boat, description="Een nieuwe deuk in de boeg."
            ).exists()
        )

    def test_logbook_requires_damage_description_when_new_damage_is_reported(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("reservations:boat-logbook", kwargs={"pk": self.reservation.pk}),
            {
                "wind_force": 3,
                "motor_hours": 12,
                "refueled": "on",
                "has_new_damage": "on",
                "new_damage_description": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Beschrijf de nieuwe schade")
        self.assertFalse(
            BoatLogbook.objects.filter(reservation=self.reservation).exists()
        )
