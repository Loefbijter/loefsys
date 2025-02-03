from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.reservations.models import Boat, Material, ReservableType


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
