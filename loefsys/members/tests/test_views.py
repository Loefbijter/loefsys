from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G

from loefsys.members.models import Skippership, UserSkippership


class UserProfileViewTestCase(TestCase):
    """Tests for the member profile views."""

    def test_profile_page_contains_edit_link(self):
        """The profile page links to the profile edit page for the logged-in user."""
        user = G(get_user_model())
        self.client.force_login(user)

        response = self.client.get(reverse("members:user-profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("members:user-profile-edit"))
        self.assertContains(response, "Profiel Bewerken")

    def test_profile_edit_page_renders_with_correct_urls(self):
        """The profile edit page renders its form and cancel links with valid URLs."""
        user = G(get_user_model())
        self.client.force_login(user)

        response = self.client.get(reverse("members:user-profile-edit"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("members:user-profile-edit"))
        self.assertContains(response, reverse("members:user-profile"))
        self.assertContains(response, "Nieuwe informatie opslaan")

    def test_profile_page_displays_skipperships_and_member_details(self):
        """The profile page renders the user's lichting, title, and skipperships."""
        user = G(get_user_model(), lichting="57e lichting", title="Assessor Bastion")
        self.client.force_login(user)
        skippership = G(Skippership, name="Kielboot")
        G(UserSkippership, user=user, skippership=skippership)

        response = self.client.get(reverse("members:user-profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "57e lichting")
        self.assertContains(response, "Assessor Bastion")
        self.assertContains(response, "Schipperschappen")
        self.assertContains(response, "Kielboot")
