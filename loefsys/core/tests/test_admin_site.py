from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G

PASSWORD = "Een-lang-wachtwoord-123"


class AdminAccessTestCase(TestCase):
    """Admin access follows from permissions instead of the staff flag."""

    def setUp(self):
        self.user = G(get_user_model(), is_staff=False, is_superuser=False)
        self.user.set_password(PASSWORD)
        self.user.save()

    def grant_permission(self):
        """Give the user a permission through a group."""
        group = Group.objects.create(name="Testgroep")
        group.permissions.add(Permission.objects.get(codename="view_event"))
        self.user.groups.add(group)

    def login_via_admin(self):
        """Submit the admin login form."""
        return self.client.post(
            reverse("admin:login"), {"username": self.user.email, "password": PASSWORD}
        )

    def test_user_without_permissions_is_refused(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)

    def test_user_with_group_permission_gets_access(self):
        self.grant_permission()
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)

    def test_staff_without_permissions_keeps_access(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)

    def test_admin_login_form_accepts_permission_holder(self):
        self.grant_permission()
        response = self.login_via_admin()
        self.assertEqual(response.status_code, 302)

    def test_admin_login_form_refuses_user_without_permissions(self):
        response = self.login_via_admin()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_inactive_user_is_refused(self):
        self.grant_permission()
        self.user.is_active = False
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)
