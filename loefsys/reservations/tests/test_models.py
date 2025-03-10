import datetime

from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.reservations.models import Boat, Material, ReservableType, Reservation
from loefsys.reservations.models.choices import Locations, ReservableCategories
from loefsys.reservations.models.reservable import ReservableItem


class BoatTestCase(TestCase):
    """Tests for Boat model creation and validation."""

    def test_create(self):
        """Test that Boat instance can be created."""
        boat = G(Boat)
        self.assertIsNotNone(boat)
        self.assertIsNotNone(boat.pk)


class MaterialTestCase(TestCase):
    """Tests for Material model creation and validation."""

    def test_create(self):
        """Test that Material instance can be created."""
        material = G(Material)
        self.assertIsNotNone(material)
        self.assertIsNotNone(material.pk)


class ReservableTypeTestCase(TestCase):
    """Tests for ReservableType model creation and validation."""

    def test_create(self):
        """Test that ReservableType instance can be created."""
        reservable_type = G(ReservableType)
        self.assertIsNotNone(reservable_type)
        self.assertIsNotNone(reservable_type.pk)


class ReservableTypePricingTestCase(TestCase):
    """Tests for ReservableTypePricing model creation and validation."""

    def test_create(self):
        """Test that ReservableTypePricing instance can be created."""
        pricing = G(ReservableType)
        self.assertIsNotNone(pricing)
        self.assertIsNotNone(pricing.pk)


class ReservationTestCase(TestCase):
    """Tests for Reservation model creation and validation."""

    def setUp(self):
        self.reservable_type = ReservableType(
            name="Room", category=ReservableCategories.ROOM, description="GiPHouse room"
        )
        self.reservable_type.save()

        self.reservable_item = ReservableItem(
            name="Reservable room",
            description="A room",
            reservable_type=self.reservable_type,
            location=Locations.KRAAIJ,
            is_reservable=True,
        )
        self.reservable_item.save()

        self.unreservable_item = ReservableItem(
            name="Unreservable room",
            description="A room",
            reservable_type=self.reservable_type,
            location=Locations.KRAAIJ,
            is_reservable=False,
        )
        self.unreservable_item.save()

    def test_create(self):
        """Tests that Reservation instance can be created."""
        reservation = Reservation(
            reserved_item=self.reservable_item,
            start=datetime.datetime(2025, 1, 1, hour=12, minute=0),
            end=datetime.datetime(2025, 1, 1, hour=13, minute=0),
        )
        reservation.save()
        self.assertIsNotNone(reservation)
        self.assertIsNotNone(reservation.pk)

    def test_same_start_end(self):
        """Tests that Reservation instance cannot be created with the same start and end time."""  # noqa: E501
        with self.assertRaises(IntegrityError):

            reservation = Reservation(
                reserved_item=self.reservable_item,
                start=datetime.datetime(2025, 1, 1, hour=12, minute=0),
                end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
            )
            reservation.save()

    def test_start_after_end(self):
        """Tests that Reservation instance cannot be created with the start after the end time."""  # noqa: E501
        with self.assertRaises(IntegrityError):

            reservation = Reservation(
                reserved_item=self.reservable_item,
                start=datetime.datetime(2025, 1, 1, hour=13, minute=0),
                end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
            )
            reservation.save()

    def test_reserved_twice(self):
        """Tests that two Reservation instances can be created for the same item on different timeslots."""  # noqa: E501
        reservation1 = Reservation(
            reserved_item=self.reservable_item,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
        )
        reservation1.save()

        reservation2 = Reservation(
            reserved_item=self.reservable_item,
            start=datetime.datetime(2025, 1, 1, hour=13, minute=0),
            end=datetime.datetime(2025, 1, 1, hour=14, minute=0),
        )
        reservation2.save()

        self.assertIsNotNone(reservation1)
        self.assertIsNotNone(reservation2)

    def test_reserved_twice_overlap(self):
        """Tests that two Reservation instances can be created for the same item on overlapping timeslots."""  # noqa: E501
        with self.assertRaises(ValidationError):
            reservation1 = Reservation(
                reserved_item=self.reservable_item,
                start=datetime.datetime(2025, 1, 1, hour=11, minute=0),
                end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
            )
            reservation1.save()
            reservation1.clean()

            reservation2 = Reservation(
                reserved_item=self.reservable_item,
                start=datetime.datetime(2025, 1, 1, hour=11, minute=30),
                end=datetime.datetime(2025, 1, 1, hour=13, minute=0),
            )
            reservation2.save()
            reservation2.clean()

    def test_duplicate(self):
        """Tests that two duplicate Reservation instances cannot be created."""
        with self.assertRaises(ValidationError):
            reservation1 = Reservation(
                reserved_item=self.reservable_item,
                start=datetime.datetime(2025, 1, 1, hour=11, minute=0),
                end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
            )
            reservation1.save()

            reservation2 = Reservation(
                reserved_item=self.reservable_item,
                start=datetime.datetime(2025, 1, 1, hour=11, minute=0),
                end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
            )
            reservation2.clean()
            reservation2.save()

    def test_reserved_two_overlap(self):
        """Tests that two Reservation instances can be created for two items on overlapping timeslots."""  # noqa: E501
        reservable_item2 = ReservableItem(
            name="big room",
            description="a room",
            reservable_type=self.reservable_type,
            location=Locations.KRAAIJ,
            is_reservable=True,
        )
        reservable_item2.save()

        reservation1 = Reservation(
            reserved_item=self.reservable_item,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
        )
        reservation1.save()

        reservation2 = Reservation(
            reserved_item=reservable_item2,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=30),
            end=datetime.datetime(2025, 1, 1, hour=13, minute=0),
        )
        reservation2.clean()
        reservation2.save()

        self.assertIsNotNone(reservation1)
        self.assertIsNotNone(reservation2)

    def is_reservable(self):
        """Tests that an item that has the is_reservable field as true can be reserved."""  # noqa: D401, E501
        reservation = Reservation(
            reserved_item=self.reservable_item,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
        )
        reservation.save()

        self.assertIsNotNone(reservation)

    def is_not_reservable(self):
        """Tests that an item that has the is_reservable field as true can be reserved."""  # noqa: D401, E501
        with self.assertRaises(ValidationError):

            reservation = Reservation(
                reserved_item=self.unreservable_item,
                start=datetime.datetime(2025, 1, 1, hour=11, minute=0),
                end=datetime.datetime(2025, 1, 1, hour=12, minute=0),
            )
            reservation.save()
