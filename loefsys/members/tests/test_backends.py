import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.groups.models import Board
from loefsys.groups.models.membership import GroupMembership

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
