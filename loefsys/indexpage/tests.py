# TODO Move all tests into a module instead of a single file.
"""Module defining the tests for indexpage."""

from datetime import datetime

from django.test import Client, TestCase
from django_dynamic_fixture import G

from loefsys.events.models import Event
from loefsys.indexpage.models import Announcement
from loefsys.users.models import User


class EventTestCase(TestCase):
    """Tests for event information display for users."""

    def setUp(self):
        """Set up user and events."""
        self.client = Client()
        self.user = G(User, email="user@user.nl", password="secret")
        G(
            Event,
            title="Bierproeverij",
            start=datetime(3000, 3, 10, 19, 0, 0),
            end=datetime(3000, 3, 10, 21, 0, 0),
            location="Café jos",
        )
        G(
            Event,
            title="Later event",
            start=datetime(5000, 1, 1, 10, 0, 0),
            end=datetime(5000, 10, 10, 10, 0, 0),
            published=True,
        )

    def test_two_events(self):
        """Test for when there are two coming events.

        Both events and their information should be displayed.
        """
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response=response, text="Bierproeverij")
        self.assertContains(
            response=response, text="10/03/3000 19:00 - 10/03/3000 21:00"
        )
        self.assertContains(response=response, text="Café jos")
        self.assertContains(response=response, text="Later event")
        self.assertContains(
            response=response, text="01/01/5000 10:00 - 10/10/5000 10:00"
        )

    def test_three_events(self):
        """Test for when there are more than two coming events.

        The two earliest coming events and their information should be displayed.
        """
        G(
            Event,
            title="Earlier event",
            start=datetime(4000, 2, 2, 20, 0, 0),
            end=datetime(4000, 12, 2, 20, 0, 0),
        )
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response=response, text="Earlier event")
        self.assertContains(
            response=response, text="02/02/4000 20:00 - 02/12/4000 20:00"
        )
        self.assertNotContains(response=response, text="Later event")
        self.assertNotContains(
            response=response, text="01/01/5000 10:00 - 10/10/5000 10:00"
        )

    def test_old_event(self):
        """Test for when there is an event that started before now.

        This old event should not be displayed.
        """
        G(
            Event,
            title="Old event",
            start=datetime(2024, 1, 1, 20, 0, 0),
            end=datetime(3000, 3, 10, 21, 0, 0),
        )
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response=response, text="Old event")
        self.assertNotContains(
            response=response, text="01/01/2024 20:00 - 10/03/3000 21:00"
        )
        self.assertContains(response=response, text="Later event")
        self.assertContains(
            response=response, text="01/01/5000 10:00 - 10/10/5000 10:00"
        )


class AnnouncementTestCase(TestCase):
    """Tests for announcement display on the index page."""

    def test_announcement_display(self):
        """Test that the announcement is displayed on the index page."""
        self.client.force_login(user=G(User))
        G(
            Announcement,
            title="Test Announcement",
            content="This is a test announcement.",
            announcement_start=datetime(2020, 1, 1, 0, 0, 0),
            announcement_end=datetime(3000, 12, 31, 23, 59, 59),
            published=True,
        )
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response=response, text="Test Announcement")
        self.assertContains(response=response, text="This is a test announcement.")

    def test_announcement_not_displayed_when_not_published(self):
        """Test that the announcement is not displayed when not published."""
        self.client.force_login(user=G(User))
        G(
            Announcement,
            title="Unpublished Announcement",
            content="This announcement should not be visible.",
            announcement_start=datetime(2020, 1, 1, 0, 0, 0),
            announcement_end=datetime(3000, 12, 31, 23, 59, 59),
            published=False,
        )
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response=response, text="Unpublished Announcement")
        self.assertNotContains(
            response=response, text="This announcement should not be visible."
        )
