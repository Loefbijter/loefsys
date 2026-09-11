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

        self.client.force_login(user)
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

        self.client.force_login(user)
        response = self.client.get(reverse("home:schippers"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "KB3")
        self.assertNotContains(response, "KB1")
        self.assertNotContains(response, "KB2")

    def test_schippers_page_truncates_extended_display_names(self):
        """Long generated names stay within a safe display length in compact lists."""
        long_first_name = "A" * 50
        long_last_name = "B" * 50
        user = G(
            get_user_model(),
            first_name=long_first_name,
            last_name=long_last_name,
            display_name_preference=0,
        )
        skippership = G(Skippership, name="KB1")
        G(UserSkippership, user=user, skippership=skippership)

        self.client.force_login(user)
        response = self.client.get(reverse("home:schippers"))

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(user.display_name), 64)
        self.assertContains(response, user.display_name)
