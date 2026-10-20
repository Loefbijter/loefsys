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
