"""Tests that draft (unpublished) events stay off the home page."""

from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event
from loefsys.members.models import User


class HomeDraftEventsTestCase(TestCase):
    """Only published upcoming events are listed on the home page."""

    def setUp(self):
        start = timezone.now() + timezone.timedelta(days=7)
        G(
            Event,
            title="Gepubliceerde testactiviteit",
            start=start,
            end=start + timezone.timedelta(hours=2),
            published=True,
        )
        G(
            Event,
            title="Geheime conceptactiviteit",
            start=start,
            end=start + timezone.timedelta(hours=2),
            published=False,
        )

    def test_active_member_does_not_see_draft_events(self):
        """An active member sees published events but not drafts."""
        self.client.force_login(G(User, is_active=True))
        response = self.client.get("/")
        self.assertContains(response, "Gepubliceerde testactiviteit")
        self.assertNotContains(response, "Geheime conceptactiviteit")
