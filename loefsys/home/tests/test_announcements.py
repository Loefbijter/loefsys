# TODO Move all tests into a module instead of a single file.
"""Module defining the tests for indexpage."""

from datetime import datetime
from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.home.models import Announcement
from loefsys.members.models import User

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
