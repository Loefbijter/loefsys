from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventRegistration
from loefsys.events.models.event import EventOrganizer


class EventTestCase(TestCase):
    """Tests for Event model creation and validation."""

    def test_create(self):
        """Test that Event instance can be created."""
        event = G(Event,
                  start="2022-01-01 00:00:00",
                  end="2023-01-01 00:00:00")
        self.assertIsNotNone(event)
        self.assertIsNotNone(event.pk)


class EventOrganizerTestCase(TestCase):
    """Tests for EventOrganizer model creation and validation."""

    def test_create(self):
        """Test that EventOrganizer instance can be created."""
        organizer = G(EventOrganizer,
                      event=G(Event,
                              start="2022-01-01 00:00:00",
                              end="2023-01-01 00:00:00"))
        self.assertIsNotNone(organizer)
        self.assertIsNotNone(organizer.pk)


class EventRegistrationTestCase(TestCase):
    """Tests for EventRegistration model creation and validation."""

    def test_create(self):
        """Test that EventRegistration instance can be created."""
        registration = G(EventRegistration,
                         event=G(Event,
                                 start="2022-01-01 00:00:00",
                                 end="2023-01-01 00:00:00"))
        self.assertIsNotNone(registration)
        self.assertIsNotNone(registration.pk)
