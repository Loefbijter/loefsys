from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G

PASSWORD = "Een-lang-wachtwoord-123"


class AdminAccessTestCase(TestCase):
    """Admin access follows from permissions instead of the staff flag."""

    def setUp(self):
        self.user = G(get_user_model(), is_superuser=False)
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

    def test_forbidden_admin_page_shows_the_site_403_page(self):
        self.grant_permission()
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:members_user_changelist"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")
        self.assertContains(response, "Geen toegang", status_code=403)

    def test_admin_permission_gives_access(self):
        self.user.user_permissions.add(
            Permission.objects.get(
                codename="access_admin", content_type__app_label="members"
            )
        )
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

    def test_superuser_gets_access(self):
        superuser = get_user_model().objects.create_superuser(
            email="super@example.com", password=PASSWORD
        )
        self.client.force_login(superuser)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)


class AdminPermissionUserListTestCase(TestCase):
    """The user list shows who holds the Admin permission directly."""

    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_superuser(
                email="super@example.com", password=PASSWORD
            )
        )
        self.admin_user = G(get_user_model(), email="beheerder@example.com")
        self.admin_user.user_permissions.add(
            Permission.objects.get(
                codename="access_admin", content_type__app_label="members"
            )
        )
        G(get_user_model(), email="lid@example.com")

    def test_filter_on_admin_permission(self):
        url = reverse("admin:members_user_changelist") + "?admin_permission=yes"
        response = self.client.get(url)
        self.assertContains(response, "beheerder@example.com")
        self.assertNotContains(response, "lid@example.com")


class AdminDashboardTestCase(TestCase):
    """The dashboard only shows what the user has permission to see."""

    def setUp(self):
        self.user = G(get_user_model(), is_superuser=False)
        self.user.user_permissions.add(
            Permission.objects.get(
                codename="view_event", content_type__app_label="events"
            )
        )
        self.client.force_login(self.user)

    def test_index_hides_cards_without_permission(self):
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="chart-events-past"')
        self.assertNotContains(response, 'id="kpi-reservations"')
        self.assertNotContains(response, 'id="kpi-pending-link"')
        self.assertNotContains(response, 'id="kpi-damage"')
        self.assertNotContains(response, 'id="kpi-skippers"')

    def test_data_leaves_out_sections_without_permission(self):
        response = self.client.get(reverse("admin:admin-dashboard-data"))
        data = response.json()
        self.assertNotIn("error", data)
        self.assertEqual(data["reservations"]["series"], [])
        self.assertEqual(data["reservations"]["pending_requests"], 0)
        self.assertEqual(data["damage"]["series"], [])
        self.assertEqual(data["skippers"]["series"], [])
        self.assertTrue(data["events"]["category_labels"])

    def test_superuser_sees_all_cards(self):
        self.client.force_login(
            get_user_model().objects.create_superuser(
                email="super@example.com", password=PASSWORD
            )
        )
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, 'id="kpi-reservations"')
        self.assertContains(response, 'id="kpi-pending-link"')
        self.assertContains(response, 'id="kpi-damage"')
        self.assertContains(response, 'id="kpi-skippers"')


class AdminWithoutSlashTestCase(TestCase):
    """``/admin`` without the trailing slash leads to the admin as well."""

    def test_admin_without_slash_redirects_to_admin(self):
        self.client.force_login(G(get_user_model(), is_superuser=True))
        response = self.client.get("/admin")
        self.assertRedirects(response, reverse("admin:index"), status_code=301)


class AdminHeaderLinkTestCase(TestCase):
    """The site header links to the admin only for users who may access it."""

    def setUp(self):
        self.user = G(get_user_model(), is_superuser=False)
        self.admin_url = reverse("admin:index")

    def test_user_without_permissions_sees_no_admin_link(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("home:home"))
        self.assertNotContains(response, f'href="{self.admin_url}"')

    def test_user_with_permission_sees_admin_link(self):
        group = Group.objects.create(name="Testgroep")
        group.permissions.add(Permission.objects.get(codename="view_event"))
        self.user.groups.add(group)
        self.client.force_login(self.user)
        response = self.client.get(reverse("home:home"))
        # Once in the desktop header and once in the phone menu.
        self.assertContains(response, f'href="{self.admin_url}"', count=2)
