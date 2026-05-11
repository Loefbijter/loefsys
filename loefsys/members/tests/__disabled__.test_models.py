from datetime import UTC, datetime
from unittest import skipUnless

from django.apps import apps
from django.core.exceptions import ValidationError
from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.members.models.skippership import Skippership
from loefsys.members.models.user import User
from loefsys.members.models.user_skippership import UserSkippership

if apps.is_installed("loefsys.reservations"):
    # Only include reservation models if the app is enabled
    from loefsys.reservations.models.boat import Boat
    from loefsys.reservations.models.choices import ReservableCategories
    from loefsys.reservations.models.reservable import ReservableType
    from loefsys.reservations.models.reservation import Reservation


class SkippershipTestCase(TestCase):
    """Tests for Skippership model creation and validation."""

    def test_create(self):
        """Test that Skippership instance can be created."""
        skippership = G(Skippership)
        self.assertIsNotNone(skippership)
        self.assertIsNotNone(skippership.pk)


class UserSkippershipTestCase(TestCase):
    """Tests for UserSkippership model creation and validation."""

    def test_create(self):
        """Test that UserSkippership instance can be created."""
        user_skippership = G(UserSkippership)
        self.assertIsNotNone(user_skippership)
        self.assertIsNotNone(user_skippership.pk)


class SkippershipModelsTestCase(TestCase):
    """Tests for skippers field in Skippership model."""

    def setUp(self):
        self.skippership1 = G(Skippership)
        self.skippership2 = G(Skippership)
        self.user1 = G(User)
        self.user2 = G(User)

    def test_multiple_user_skippership(self):
        """Test that multiple users can be contained in the skippers field."""
        G(UserSkippership, user=self.user1, skippership=self.skippership1)
        G(UserSkippership, user=self.user2, skippership=self.skippership1)
        self.assertIn(self.user1, self.skippership1.skippers.all())
        self.assertIn(self.user2, self.skippership1.skippers.all())

    def test_multiple_skippership_user(self):
        """Test that a user can be contained in multiple skippership skippers fields."""
        G(UserSkippership, user=self.user2, skippership=self.skippership2)
        self.assertNotIn(self.user1, self.skippership2.skippers.all())
        self.assertIn(self.user2, self.skippership2.skippers.all())

    def test_no_user_skippership(self):
        """Test that skipperships can have empty skippers' fields."""
        skippership3 = G(Skippership)
        self.assertEqual(skippership3.skippers.count(), 0)

    def test_no_skippership_user(self):
        """Test that a user does not automatically get added to a skippership."""
        user3 = G(User)
        self.assertNotIn(user3, self.skippership1.skippers.all())
        self.assertNotIn(user3, self.skippership2.skippers.all())


@skipUnless(
    apps.is_installed("loefsys.reservations"), "Tests depend on reservation models"
)
class ReservationUserSkippershipTestCase(TestCase):
    """Tests for authorized_skipper field in Reservation model."""

    def setUp(self):
        self.user1 = G(User)
        self.user2 = G(User)
        self.skippership = G(Skippership, name="Kielboot 2")
        self.userskippership = G(
            UserSkippership, user=self.user2, skippership=self.skippership
        )
        self.reservable_type = G(
            ReservableType, name="Kielboten", category=ReservableCategories.BOAT
        )
        self.boat = G(
            Boat,
            name="Kielboot",
            reservable_type=self.reservable_type,
            requires_skippership=self.skippership,
        )

    def test_reservation_authorized_userskippership(self):
        """Test that a reservation can be created with an authorized skipper."""
        reservation = G(
            Reservation,
            reserved_item=self.boat,
            reservee_user=self.user1,
            start=datetime(2025, 1, 1, hour=11, minute=0, tzinfo=UTC),
            end=datetime(2025, 1, 1, hour=12, minute=0, tzinfo=UTC),
            authorized_userskippership=self.userskippership,
        )
        self.assertIsNotNone(reservation)

    def test_reservation_no_authorized_userskippership(self):
        """Test that a reservation cannot be made without an authorized skipper."""
        reservation = G(
            Reservation,
            reserved_item=self.boat,
            reservee_user=self.user1,
            start=datetime(2025, 1, 1, hour=11, minute=0, tzinfo=UTC),
            end=datetime(2025, 1, 1, hour=12, minute=0, tzinfo=UTC),
            authorized_userskippership=None,
        )
        with self.assertRaises(ValidationError):
            reservation.clean()

    def test_reservation_unauthorized_userskippership(self):
        """Test that a reservation cannot be made with an unauthorized skipper."""
        user3 = G(User)
        skippership = G(Skippership, name="Kielboot 1")
        userskippership = G(UserSkippership, user=user3, skippership=skippership)
        reservation = G(
            Reservation,
            reserved_item=self.boat,
            reservee_user=self.user1,
            start=datetime(2025, 1, 1, hour=11, minute=0, tzinfo=UTC),
            end=datetime(2025, 1, 1, hour=12, minute=0, tzinfo=UTC),
            authorized_userskippership=userskippership,
        )
        with self.assertRaises(ValidationError):
            reservation.clean()

    def test_reservation_no_skippership(self):
        """Test that a reservation can be made with an authorized skipper without the reserved item requiring a skippership."""  # noqa: E501
        boat2 = G(Boat)
        reservation = G(
            Reservation,
            reserved_item=boat2,
            reservee_user=self.user1,
            start=datetime(2025, 1, 1, hour=11, minute=0, tzinfo=UTC),
            end=datetime(2025, 1, 1, hour=12, minute=0, tzinfo=UTC),
            authorized_userskippership=self.userskippership,
        )
        self.assertIsNotNone(reservation)
