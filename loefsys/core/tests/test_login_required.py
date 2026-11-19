from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G


class LoginRequiredTestCase(TestCase):
    """Every page needs a login, except the views marked as public."""

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(reverse("members:user-profile"))
        self.assertRedirects(
            response,
            f"{reverse('members:login')}?next={reverse('members:user-profile')}",
            fetch_redirect_response=False,
        )

    def test_public_pages_are_reachable_without_login(self):
        for name in (
            "login",
            "members:login",
            "members:reset-password",
            "members:reset-password-done",
            "password_reset_complete",
        ):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_reset_link_is_reachable_without_login(self):
        url = reverse(
            "password_reset_confirm", kwargs={"uidb64": "MQ", "token": "invalid"}
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_language_can_be_chosen_without_login(self):
        response = self.client.post(
            reverse("set_language"), {"language": "en", "next": "/login/"}
        )
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)

    def test_admin_login_is_reachable_without_login(self):
        self.assertEqual(self.client.get(reverse("admin:login")).status_code, 200)


class NoStoreForAuthenticatedTestCase(TestCase):
    """Pages for logged-in users must not be cached by the browser."""

    def test_authenticated_pages_are_not_cached(self):
        self.client.force_login(G(get_user_model()))
        response = self.client.get(reverse("members:user-profile"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_anonymous_pages_are_left_alone(self):
        response = self.client.get(reverse("members:login"))
        self.assertFalse(response.has_header("Pragma"))
