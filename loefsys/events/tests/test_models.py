from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventRegistration
from loefsys.events.models.choices import EventCategories, RegistrationStatus
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


class EventQueueTestCase(TestCase):
    """The queue catches up when places open up on an event."""

    def setUp(self):
        now = timezone.now()
        self.event = G(
            Event,
            capacity=2,
            start=now + timedelta(days=30),
            end=now + timedelta(days=30, hours=3),
            registration_start=now - timedelta(days=1),
            registration_deadline=now + timedelta(days=20),
            cancelation_deadline=now + timedelta(days=20),
        )
        self.registrations = [
            G(EventRegistration, event=self.event, added_by_organizer=False)
            for _ in range(5)
        ]

    def statuses(self):
        return [
            EventRegistration.objects.get(pk=registration.pk).status
            for registration in self.registrations
        ]

    def test_full_event_queues_the_rest(self):
        self.assertEqual(
            self.statuses(),
            [RegistrationStatus.ACTIVE] * 2 + [RegistrationStatus.QUEUED] * 3,
        )

    def test_raising_capacity_activates_queue_in_order(self):
        self.event.capacity = 4
        self.event.save()
        self.assertEqual(
            self.statuses(),
            [RegistrationStatus.ACTIVE] * 4 + [RegistrationStatus.QUEUED],
        )

    def test_new_registration_after_raise_is_queued_behind_waiting_members(self):
        self.event.capacity = 3
        self.event.save()
        late = G(EventRegistration, event=self.event, added_by_organizer=False)
        self.assertEqual(late.status, RegistrationStatus.QUEUED)
        self.assertEqual(late.get_queue_position, 3)

    def test_removing_capacity_activates_whole_queue(self):
        self.event.capacity = None
        self.event.save()
        self.assertEqual(self.statuses(), [RegistrationStatus.ACTIVE] * 5)

    def test_lowering_capacity_keeps_active_registrations(self):
        self.event.capacity = 1
        self.event.save()
        self.assertEqual(
            self.statuses(),
            [RegistrationStatus.ACTIVE] * 2 + [RegistrationStatus.QUEUED] * 3,
        )

    def test_cancellation_activates_first_in_queue(self):
        self.registrations[0].cancel()
        statuses = self.statuses()
        self.assertEqual(
            statuses[1:],
            [RegistrationStatus.ACTIVE] * 2 + [RegistrationStatus.QUEUED] * 2,
        )
