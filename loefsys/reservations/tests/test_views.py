import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from loefsys.members.models import User
from loefsys.reservations.models import Reservable, ReservableType, Reservation
from loefsys.reservations.models.choices import Locations, ReservableCategories


class ReservationDeleteViewTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="secure-password",
            first_name="Olga",
            last_name="Owner",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="secure-password",
            first_name="Otto",
            last_name="Other",
        )
        reservable_type = ReservableType.objects.create(
            name="Room", category=ReservableCategories.ROOM, description="A room"
        )
        reservable = Reservable.objects.create(
            name="Test room",
            description="A room",
            type=reservable_type,
            location=Locations.KRAAIJ,
            is_reservable=True,
        )
        self.reservation = Reservation.objects.create(
            reservable=reservable,
            user=self.owner,
            start=timezone.now() + datetime.timedelta(days=1),
            end=timezone.now() + datetime.timedelta(days=1, hours=2),
        )
        self.url = reverse(
            "reservations:reservation-delete", kwargs={"pk": self.reservation.pk}
        )

    def test_owner_can_delete(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("reservations:reservations"),
            fetch_redirect_response=False,
        )
        self.assertFalse(Reservation.objects.filter(pk=self.reservation.pk).exists())

    def test_other_member_cannot_view_delete_page(self):
        self.client.force_login(self.other)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_other_member_cannot_delete(self):
        self.client.force_login(self.other)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Reservation.objects.filter(pk=self.reservation.pk).exists())


class CheckAvailabilityTestCase(TestCase):
    def setUp(self):
        self.client.force_login(
            User.objects.create_user(
                email="member@example.com",
                password="secure-password",
                first_name="Mila",
                last_name="Member",
            )
        )
        reservable_type = ReservableType.objects.create(
            name="Laser", category=ReservableCategories.BOAT, description="A dinghy"
        )
        self.free_boat = Reservable.objects.create(
            name="Zeemeeuw",
            description="A dinghy",
            type=reservable_type,
            location=Locations.BASTION,
            is_reservable=True,
        )
        self.boat_in_maintenance = Reservable.objects.create(
            name="Kokmeeuw",
            description="A dinghy",
            type=reservable_type,
            location=Locations.BASTION,
            is_reservable=False,
        )
        self.params = {"start": "2030-06-01T10:00", "end": "2030-06-01T12:00"}

    def check(self, reservable, url_path="check-availability"):
        response = self.client.get(
            f"/reservations/{url_path}",
            {**self.params, "reservable": reservable.pk, "object_pk": 0},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["available"]

    def test_free_item_is_available(self):
        self.assertTrue(self.check(self.free_boat))
        self.assertTrue(self.check(self.free_boat, "update/check-availability"))

    def test_item_in_maintenance_is_not_available(self):
        self.assertFalse(self.check(self.boat_in_maintenance))
        self.assertFalse(
            self.check(self.boat_in_maintenance, "update/check-availability")
        )
