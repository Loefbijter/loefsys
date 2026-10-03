"""Tests for who sees draft (unpublished) events on the home page."""

from datetime import timedelta

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventOrganizer
from loefsys.groups.models import Board, Committee
from loefsys.groups.models.membership import GroupMembership
from loefsys.members.models import User


class HomeDraftEventsTestCase(TestCase):
    """Drafts are hidden from members but shown to the board and organizers."""

    def setUp(self):
        start = timezone.now() + timedelta(days=7)
        G(
            Event,
            title="Gepubliceerde testactiviteit",
            start=start,
            end=start + timedelta(hours=2),
            published=True,
        )
        self.draft = G(
            Event,
            title="Geheime conceptactiviteit",
            start=start,
            end=start + timedelta(hours=2),
            published=False,
        )

    def assert_sees_draft(self, user, sees_draft):
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertContains(response, "Gepubliceerde testactiviteit")
        if sees_draft:
            self.assertContains(response, "Geheime conceptactiviteit")
        else:
            self.assertNotContains(response, "Geheime conceptactiviteit")

    def test_member_does_not_see_draft_events(self):
        """An active member sees published events but not drafts."""
        self.assert_sees_draft(G(User, is_active=True), sees_draft=False)

    def test_board_member_sees_draft_events(self):
        """A current board member sees drafts."""
        user = G(User)
        G(GroupMembership, user=user, group=G(Board), member_until=None)
        self.assert_sees_draft(user, sees_draft=True)

    def test_former_board_member_does_not_see_draft_events(self):
        """A board membership that has ended no longer shows drafts."""
        user = G(User)
        G(
            GroupMembership,
            user=user,
            group=G(Board),
            member_until=timezone.now().date() - timedelta(days=1),
        )
        self.assert_sees_draft(user, sees_draft=False)

    def test_user_with_change_event_permission_sees_draft_events(self):
        """Anyone who may change events sees drafts."""
        user = G(User)
        user.user_permissions.add(Permission.objects.get(codename="change_event"))
        self.assert_sees_draft(user, sees_draft=True)

    def test_organizer_sees_own_draft_event(self):
        """An organizer sees the draft they organize."""
        user = G(User)
        G(EventOrganizer, event=self.draft).user.add(user)
        self.assert_sees_draft(user, sees_draft=True)

    def test_organizing_committee_member_sees_draft_event(self):
        """A member of the organizing committee sees the draft."""
        user = G(User)
        committee = G(Committee)
        G(GroupMembership, user=user, group=committee, member_until=None)
        G(EventOrganizer, event=self.draft).groups.add(committee)
        self.assert_sees_draft(user, sees_draft=True)
