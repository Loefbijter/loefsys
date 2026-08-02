from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G

from loefsys.members.models import Skippership, UserSkippership


class SchippersViewTestCase(TestCase):
    """Tests for the schippers page grouping logic."""

    def test_schippers_page_displays_non_kb_skipperships(self):
        """The page includes skipperships that are not part of a KB hierarchy."""
        user = G(get_user_model())
        skippership = G(Skippership, name="Kielboot")
        G(UserSkippership, user=user, skippership=skippership)

        response = self.client.get(reverse("home:schippers"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kielboot")

    def test_schippers_page_shows_only_the_furthest_child_in_a_chain(self):
        """Users are listed under the deepest skippership in a parent chain."""
        user = G(get_user_model())
        first = G(Skippership, name="KB1")
        second = G(Skippership, name="KB2", parent=first)
        third = G(Skippership, name="KB3", parent=second)
        G(UserSkippership, user=user, skippership=first)
        G(UserSkippership, user=user, skippership=second)
        G(UserSkippership, user=user, skippership=third)

        response = self.client.get(reverse("home:schippers"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "KB3")
        self.assertNotContains(response, "KB1")
        self.assertNotContains(response, "KB2")
