from datetime import timedelta
from unittest import skipUnless

from django.apps import apps
from django.test import Client, TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventRegistration
from loefsys.events.models.choices import EventCategories, RegistrationStatus
from loefsys.home.views import HomeView
from loefsys.members.models import User

TRAINING = EventCategories.TRAINING


def evening(days_ahead: int, **fields) -> Event:
    """Create a published event from 19:00 to 21:00, ``days_ahead`` days from now."""
    start = (timezone.localtime() + timedelta(days=days_ahead)).replace(
        hour=19, minute=0, second=0, microsecond=0
    )
    return G(
        Event, start=start, end=start + timedelta(hours=2), published=True, **fields
    )


@skipUnless(apps.is_installed("loefsys.events"), "Events app not installed")
class EventTestCase(TestCase):
    """Tests for the upcoming events on the home page."""

    def setUp(self):
        """Log in a member."""
        self.client = Client()
        self.user = G(User, email="user@user.nl", password="secret")
        self.client.force_login(self.user)

    def test_two_events(self):
        """Upcoming events are listed with their time and location."""
        evening(3, title="Bierproeverij", location="Café jos")
        evening(10, title="Later event")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bierproeverij")
        self.assertContains(response, "Café jos")
        self.assertContains(response, "19:00\N{EN DASH}21:00")
        self.assertContains(response, "Later event")

    def test_three_events(self):
        """Only the first few upcoming events are listed, earliest first."""
        limit = HomeView.UPCOMING_LIMIT
        for day in range(1, limit + 2):
            evening(day, title=f"Event on day {day}")

        response = self.client.get("/")

        shown = [event.title for event in response.context["upcoming_events"]]
        self.assertEqual(shown, [f"Event on day {day}" for day in range(1, limit + 1)])
        self.assertNotContains(response, f"Event on day {limit + 1}")

    def test_old_event(self):
        """An event that has already started is not listed."""
        now = timezone.now()
        G(
            Event,
            title="Old event",
            start=now - timedelta(days=1),
            end=now + timedelta(days=1),
            published=True,
        )
        evening(3, title="Later event")

        response = self.client.get("/")

        self.assertNotContains(response, "Old event")
        self.assertContains(response, "Later event")


class UpcomingEventsFilterTestCase(TestCase):
    """Members can filter the upcoming events on the home page."""

    def setUp(self):
        self.user = G(User, email="lid@example.com")
        self.client.force_login(self.user)
        self.training = evening(1, title="Kielboottraining", category=TRAINING)
        self.borrel = evening(2, title="Borrel", category=EventCategories.LEISURE)
        self.full_training = evening(
            3, title="Volle training", category=TRAINING, capacity=1
        )
        G(
            EventRegistration,
            event=self.full_training,
            contact=G(User, email="ander@example.com"),
            status=RegistrationStatus.ACTIVE,
        )

    def shown(self, query=""):
        response = self.client.get(f"/{query}")
        return [event.title for event in response.context["upcoming_events"]]

    def test_default_shows_everything(self):
        self.assertEqual(self.shown(), ["Kielboottraining", "Borrel", "Volle training"])

    def test_only_trainings(self):
        self.assertEqual(
            self.shown("?events=trainings"), ["Kielboottraining", "Volle training"]
        )

    def test_only_other_activities(self):
        self.assertEqual(self.shown("?events=other"), ["Borrel"])

    def test_hide_full_events(self):
        self.assertEqual(
            self.shown("?events=all&full=hide"), ["Kielboottraining", "Borrel"]
        )
        self.assertEqual(
            self.shown("?events=trainings&full=hide"), ["Kielboottraining"]
        )

    def test_full_event_you_are_registered_for_stays(self):
        # The earliest registration is the "next event" hero, not part of the list.
        G(
            EventRegistration,
            event=self.training,
            contact=self.user,
            status=RegistrationStatus.ACTIVE,
        )
        G(
            EventRegistration,
            event=self.full_training,
            contact=self.user,
            status=RegistrationStatus.QUEUED,
        )
        self.assertEqual(self.shown("?full=hide"), ["Borrel", "Volle training"])

    def test_unknown_filter_falls_back_to_all(self):
        self.assertEqual(len(self.shown("?events=nonsense")), 3)

    def test_filter_links_keep_the_other_choice(self):
        response = self.client.get("/?events=trainings&full=hide")
        self.assertContains(response, 'href="?events=other&amp;full=hide"')
        self.assertContains(response, 'href="?events=trainings"')
