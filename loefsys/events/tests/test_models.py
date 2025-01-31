from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventRegistration, MandatoryRegistrationDetails
from loefsys.events.models.event import EventOrganizer


class EventTestCase(TestCase):
    """Tests for Event model creation and validation."""

    def test_create(self):
        """Test that Event instance can be created."""
        event = G(Event)
        self.assertIsNotNone(event)
        self.assertIsNotNone(event.pk)


class MandatoryRegistrationDetailsTestCase(TestCase):
    """Tests for MandatoryRegistrationDetails model creation and validation."""

    def test_create(self):
        """Test that MandatoryRegistrationDetails instance can be created."""
        details = G(MandatoryRegistrationDetails)
        self.assertIsNotNone(details)
        self.assertIsNotNone(details.pk)


class EventOrganizerTestCase(TestCase):
    """Tests for EventOrganizer model creation and validation."""

    def test_create(self):
        """Test that EventOrganizer instance can be created."""
        organizer = G(EventOrganizer)
        self.assertIsNotNone(organizer)
        self.assertIsNotNone(organizer.pk)


class EventRegistrationTestCase(TestCase):
    """Tests for EventRegistration model creation and validation."""

    def test_create(self):
        """Test that EventRegistration instance can be created."""
        registration = G(EventRegistration)
        self.assertIsNotNone(registration)
        self.assertIsNotNone(registration.pk)
