import datetime
from importlib import import_module

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import IntegrityError, connection, transaction
from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.groups.models import Board
from loefsys.groups.models.membership import GroupMembership

lowercase_emails = import_module(
    "loefsys.members.migrations.0012_lowercase_email"
).lowercase_emails

PERM = "events.change_event"


class LoefbijterGroupBackendTestCase(TestCase):
    """Permissions of Loefbijter groups apply to their current members."""

    def setUp(self):
        self.today = datetime.date.today()
        self.board = G(
            Board,
            name="Testbestuur",
            date_foundation=self.today - datetime.timedelta(days=30),
            date_discontinuation=None,
        )
        self.board.permissions.add(Permission.objects.get(codename="change_event"))
        self.user = G(get_user_model(), is_superuser=False)

    def fresh_user(self):
        """Reload the user to drop the cached permissions."""
        return get_user_model().objects.get(pk=self.user.pk)

    def add_membership(self, **kwargs):
        """Add the user to the board."""
        kwargs.setdefault("member_since", self.today - datetime.timedelta(days=1))
        GroupMembership.objects.create(user=self.user, group=self.board, **kwargs)

    def test_no_permission_without_membership(self):
        self.assertFalse(self.fresh_user().has_perm(PERM))

    def test_active_membership_grants_permission(self):
        self.add_membership()
        user = self.fresh_user()
        self.assertTrue(user.has_perm(PERM))
        self.assertTrue(user.has_module_perms("events"))

    def test_ended_membership_grants_nothing(self):
        self.add_membership(member_until=self.today - datetime.timedelta(days=1))
        self.assertFalse(self.fresh_user().has_perm(PERM))

    def test_discontinued_group_grants_nothing(self):
        self.add_membership()
        self.board.date_discontinuation = self.today - datetime.timedelta(days=1)
        self.board.save()
        self.assertFalse(self.fresh_user().has_perm(PERM))

    def test_loefbijter_groups_field_grants_permission(self):
        self.user.loefbijter_groups.add(self.board)
        self.assertTrue(self.fresh_user().has_perm(PERM))

    def test_django_groups_still_work(self):
        group = Group.objects.create(name="Testgroep")
        group.permissions.add(Permission.objects.get(codename="view_event"))
        self.user.groups.add(group)
        self.assertTrue(self.fresh_user().has_perm("events.view_event"))

    def test_login_still_works(self):
        self.user.set_password("Een-lang-wachtwoord-123")
        self.user.save()
        self.assertTrue(
            self.client.login(
                username=self.user.email, password="Een-lang-wachtwoord-123"
            )
        )


class EmailLoginCaseTestCase(TestCase):
    """Logging in ignores the capitalisation of the email address."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "jan.zeiler@example.com", "geheim-wachtwoord"
        )

    def test_login_with_different_case(self):
        self.assertTrue(
            self.client.login(
                username="Jan.Zeiler@Example.COM", password="geheim-wachtwoord"
            )
        )

    def test_login_form_with_different_case(self):
        response = self.client.post(
            "/login/",
            {"username": "JAN.ZEILER@EXAMPLE.COM", "password": "geheim-wachtwoord"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_wrong_password_still_fails(self):
        self.assertFalse(
            self.client.login(username="JAN.ZEILER@example.com", password="fout")
        )

    def test_email_is_stored_in_lowercase(self):
        user = get_user_model().objects.create_user("Piet.Wind@Example.COM", "x")
        self.assertEqual(user.email, "piet.wind@example.com")
        user.refresh_from_db()
        self.assertEqual(user.email, "piet.wind@example.com")
        self.assertTrue(
            get_user_model().objects.filter(email="PIET.WIND@example.com").exists()
        )

    def test_address_differing_only_in_case_is_taken(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            get_user_model().objects.create_user("JAN.ZEILER@example.com", "x")


class LowercaseEmailMigrationTestCase(TestCase):
    """The migration lowercases existing addresses and refuses on clashes."""

    def set_raw_email(self, user, email):
        # Bypass the field's lowercasing to recreate data from before it.
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {user._meta.db_table} SET email = %s WHERE id = %s",
                [email, user.pk],
            )

    def test_lowercases_existing_addresses(self):
        user = G(get_user_model())
        self.set_raw_email(user, "Oud.Lid@Example.com")
        lowercase_emails(apps, None)
        user.refresh_from_db()
        self.assertEqual(user.email, "oud.lid@example.com")

    def test_refuses_when_addresses_clash(self):
        first, second = G(get_user_model()), G(get_user_model())
        self.set_raw_email(first, "Dubbel@example.com")
        self.set_raw_email(second, "dubbel@example.com")
        with self.assertRaisesMessage(RuntimeError, "Dubbel@example.com"):
            lowercase_emails(apps, None)
