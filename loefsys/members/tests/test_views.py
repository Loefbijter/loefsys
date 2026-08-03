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

    def test_profile_page_shows_only_furthest_child_skippership(self):
        """If a user has multiple skipperships in a parent chain.

        show only the deepest one.
        """
        user = G(get_user_model())
        self.client.force_login(user)
        first = G(Skippership, name="KB1")
        second = G(Skippership, name="KB2", parent=first)
        G(UserSkippership, user=user, skippership=first)
        G(UserSkippership, user=user, skippership=second)

        response = self.client.get(reverse("members:user-profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "KB2")
        self.assertNotContains(response, "KB1")

    def test_profile_edit_page_saves_pod_link_without_showing_it_publicly(self):
        """The profile edit form stores a POD link privately and it stays.

        off the public profile.
        """
        user = G(get_user_model())
        self.client.force_login(user)
        pod_kb_link = "https://docs.google.com/spreadsheets/d/example_kb/edit"
        pod_zb_link = "https://docs.google.com/spreadsheets/d/example_zb/edit"

        response = self.client.post(
            reverse("members:user-profile-edit"),
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "initials": user.initials,
                "nickname": user.nickname,
                "display_name_preference": user.display_name_preference,
                "pod_kb_link": pod_kb_link,
                "pod_zb_link": pod_zb_link,
                "gender": user.gender,
                "birthday": user.birthday or "",
                "show_birthday": user.show_birthday,
                "note": user.note,
            },
        )

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.pod_kb_link, pod_kb_link)
        self.assertEqual(user.pod_zb_link, pod_zb_link)

        profile_response = self.client.get(reverse("members:user-profile"))

        self.assertEqual(profile_response.status_code, 200)
        self.assertNotContains(profile_response, pod_kb_link)
        self.assertNotContains(profile_response, pod_zb_link)
