from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventRegistration


class EventDetailAttendeesTestCase(TestCase):
    """Tests for the attendee grid on the event detail page."""

    def setUp(self):
        now = timezone.now()
        self.event = G(
            Event,
            start=now + timezone.timedelta(days=7),
            end=now + timezone.timedelta(days=7, hours=2),
            registration_start=now - timezone.timedelta(days=1),
            registration_deadline=now + timezone.timedelta(days=6),
            cancelation_deadline=now + timezone.timedelta(days=6),
            published=True,
        )
        self.attendee = G(get_user_model())
        G(EventRegistration, event=self.event, contact=self.attendee)
        self.viewer = G(get_user_model())
        self.client.force_login(self.viewer)

    def test_attendees_hidden_without_permission(self):
        """Attendee grid should not render without the view_eventregistration perm."""
        response = self.client.get(self.event.get_absolute_url())
        self.assertFalse(response.context["can_view_attendees"])

    def test_attendees_visible_with_permission(self):
        """Attendee grid renders for users with the view_eventregistration perm."""
        perm = Permission.objects.get(codename="view_eventregistration")
        self.viewer.user_permissions.add(perm)
        response = self.client.get(self.event.get_absolute_url())
        self.assertTrue(response.context["can_view_attendees"])
        self.assertIn(self.attendee, [r.contact for r in response.context["attendees"]])
