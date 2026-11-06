from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventRegistration
from loefsys.events.models.choices import EventCategories
from loefsys.events.models.event import EventOrganizer


class EventTestCase(TestCase):
    """Tests for Event model creation and validation."""

    def test_create(self):
        """Test that Event instance can be created."""
        event = G(
            Event,
            start="2022-01-01 00:00:00+00:00",
            registration_deadline="2021-12-31 00:00:00+00:00",
            end="2023-01-01 00:00:00+00:00",
        )
        self.assertIsNotNone(event)
        self.assertIsNotNone(event.pk)

    def test_registration_deadline_is_required(self):
        """An event without a registration deadline doesn't validate.

        Without a deadline, registration never opens, so forms must ask for one.
        """
        start = timezone.now() + timedelta(days=7)
        event = Event(
            title="Zeilweekend",
            slug="zeilweekend",
            description="",
            start=start,
            end=start + timedelta(hours=2),
            category=EventCategories.TRAINING,
            location="Haven",
        )
        with self.assertRaises(ValidationError) as caught:
            event.full_clean()
        self.assertIn("registration_deadline", caught.exception.message_dict)

        event.registration_deadline = start - timedelta(days=1)
        event.full_clean()


class EventOrganizerTestCase(TestCase):
    """Tests for EventOrganizer model creation and validation."""

    def test_create(self):
        """Test that EventOrganizer instance can be created."""
        organizer = G(
            EventOrganizer,
            event=G(
                Event,
                start="2022-01-01 00:00:00+00:00",
                registration_deadline="2021-12-31 00:00:00+00:00",
                end="2023-01-01 00:00:00+00:00",
            ),
        )
        self.assertIsNotNone(organizer)
        self.assertIsNotNone(organizer.pk)


class EventRegistrationTestCase(TestCase):
    """Tests for EventRegistration model creation and validation."""

    def test_create(self):
        """Test that EventRegistration instance can be created."""
        registration = G(
            EventRegistration,
            event=G(
                Event,
                start="2022-01-01 00:00:00+00:00",
                registration_deadline="2021-12-31 00:00:00+00:00",
                end="2023-01-01 00:00:00+00:00",
            ),
        )
        self.assertIsNotNone(registration)
        self.assertIsNotNone(registration.pk)
