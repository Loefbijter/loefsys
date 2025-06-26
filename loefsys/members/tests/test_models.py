import datetime
from datetime import date

from django.forms import ValidationError
from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.members.models.address import Address
from loefsys.members.models.member import MemberDetails
from loefsys.members.models.membership import Membership, validate_has_overlap
from loefsys.members.models.skippership import Skippership
from loefsys.members.models.study_registration import StudyRegistration
from loefsys.members.models.user import User
from loefsys.members.models.user_skippership import UserSkippership
from loefsys.reservations.models.boat import Boat
from loefsys.reservations.models.choices import ReservableCategories
from loefsys.reservations.models.reservable import ReservableType
from loefsys.reservations.models.reservation import Reservation


class AddressTestCase(TestCase):
    """Tests for Address model creation and validation."""

    def test_create(self):
        """Test that Address instance can be created."""
        address = G(Address)
        self.assertIsNotNone(address)
        self.assertIsNotNone(address.pk)


class MemberDetailsTestCase(TestCase):
    """Tests for Member model creation and validation."""

    def test_create(self):
        """Test that Member instance can be created."""
        member = G(MemberDetails)
        self.assertIsNotNone(member)
        self.assertIsNotNone(member.pk)


class MembershipTestCase(TestCase):
    """Tests for Membership model creation and validation."""

    def test_create(self):
        """Test that Membership instance can be created."""
        membership = G(Membership)
        self.assertIsNotNone(membership)
        self.assertIsNotNone(membership.pk)


class StudyRegistrationTestCase(TestCase):
    """Tests for StudyRegistration model creation and validation."""

    def test_create(self):
        """Test that StudyRegistration instance can be created."""
        registration = G(StudyRegistration)
        self.assertIsNotNone(registration)
        self.assertIsNotNone(registration.pk)


class MembershipOverlapTestCase(TestCase):
    """Tests for the validate_overlap function in the Membership model."""

    def setUp(self):
        self.member = G(MemberDetails)

    def test_no_overlap(self):
        """Test that there is no overlap when the membership dates don't overlap."""
        membership1 = G(
            Membership,
            member=self.member,
            start=date(2024, 1, 1),
            end=date(2024, 12, 31),
        )
        membership2 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        self.assertFalse(validate_has_overlap(membership1, [membership2]))

    def test_overlap(self):
        """Test that there is overlap when the membership dates overlap."""
        membership1 = G(
            Membership, member=self.member, start=date(2023, 6, 1), end=date(2024, 6, 1)
        )
        membership2 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        self.assertTrue(validate_has_overlap(membership1, [membership2]))

    def test_overlap_same_start(self):
        """Test that there is overlap when the membership has the same start date."""
        membership1 = G(
            Membership, member=self.member, start=date(2023, 1, 1), end=date(2024, 6, 1)
        )
        membership2 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        self.assertTrue(validate_has_overlap(membership1, [membership2]))

    def test_overlap_same_end(self):
        """Test that there is overlap when the membership has the same end date."""
        membership1 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        membership2 = G(
            Membership,
            member=self.member,
            start=date(2022, 1, 1),
            end=date(2023, 12, 31),
        )
        self.assertTrue(validate_has_overlap(membership1, [membership2]))

    def test_no_overlap_null_end(self):
        """Test that there is no overlap when an ongoing membership has no end date."""
        membership1 = G(
            Membership, member=self.member, start=date(2024, 1, 1), end=None
        )
        membership2 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        self.assertFalse(validate_has_overlap(membership1, [membership2]))

    def test_overlap_null_end(self):
        """Test that there is overlap with an ongoing membership."""
        membership1 = G(
            Membership, member=self.member, start=date(2023, 6, 1), end=None
        )
        membership2 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        self.assertTrue(validate_has_overlap(membership1, [membership2]))

    def test_no_overlap_multiple_memberships(self):
        """Test that no overlap occurs with non-overlapping multiple memberships."""
        membership1 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        membership2 = G(
            Membership,
            member=self.member,
            start=date(2024, 1, 1),
            end=date(2024, 12, 31),
        )
        membership3 = G(
            Membership,
            member=self.member,
            start=date(2020, 1, 1),
            end=date(2020, 12, 31),
        )
        self.assertFalse(validate_has_overlap(membership1, [membership2, membership3]))

    def test_overlap_multiple_memberships(self):
        """Test that there is overlap with multiple overlapping memberships."""
        membership1 = G(
            Membership, member=self.member, start=date(2023, 6, 1), end=date(2024, 6, 1)
        )
        membership2 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        membership3 = G(
            Membership,
            member=self.member,
            start=date(2020, 1, 1),
            end=date(2020, 12, 31),
        )
        self.assertTrue(validate_has_overlap(membership1, [membership2, membership3]))

    def test_overlap_same_dates(self):
        """Test that there is overlap with matching start and end dates."""
        membership1 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        membership2 = G(
            Membership,
            member=self.member,
            start=date(2023, 1, 1),
            end=date(2023, 12, 31),
        )
        self.assertTrue(validate_has_overlap(membership1, [membership2]))


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
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
            authorized_userskippership=self.userskippership,
        )
        self.assertIsNotNone(reservation)

    def test_reservation_no_authorized_userskippership(self):
        """Test that a reservation cannot be made without an authorized skipper."""
        reservation = G(
            Reservation,
            reserved_item=self.boat,
            reservee_user=self.user1,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC),
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
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC),
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
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
            authorized_userskippership=self.userskippership,
        )
        self.assertIsNotNone(reservation)
