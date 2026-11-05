"""Tests for who may evaluate reservation requests, see reservations.permissions."""

import datetime

from django.contrib.auth.models import Permission
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from loefsys.groups.models import LoefbijterGroup
from loefsys.groups.models.membership import GroupMembership
from loefsys.members.models import User
from loefsys.reservations.models import Reservable, ReservableType, Reservation
from loefsys.reservations.models.choices import ReservableCategories
from loefsys.reservations.permissions import can_evaluate, manages_reservables


def make_user(name, **extra):
    """Create a user called ``name``."""
    return User.objects.create_user(
        email=f"{name}@example.com",
        password="secure-password",
        first_name=name.capitalize(),
        last_name="Test",
        **extra,
    )


class ManagedReservablesTestCase(TestCase):
    """Members, a committee and reservables with and without a manager."""

    member: User
    manager: User
    handler: User
    superuser: User
    committee: LoefbijterGroup
    unmanaged: Reservable
    by_person: Reservable
    by_group: Reservable

    @classmethod
    def setUpTestData(cls):
        cls.member = make_user("member")
        cls.manager = make_user("manager")
        cls.handler = make_user("handler")
        cls.handler.user_permissions.add(
            Permission.objects.get(codename="change_reservation")
        )
        cls.superuser = make_user("root", is_superuser=True)
        cls.committee = LoefbijterGroup.objects.create(
            name="Botencommissie",
            date_foundation=datetime.date(2000, 1, 1),
            display_members=True,
        )

        room_type = ReservableType.objects.create(
            name="Room", category=ReservableCategories.ROOM, description="A room"
        )
        cls.unmanaged = Reservable.objects.create(
            name="Unmanaged room", description="", type=room_type
        )
        cls.by_person = Reservable.objects.create(
            name="Person's room",
            description="",
            type=room_type,
            managed_by_user=cls.manager,
        )
        cls.by_group = Reservable.objects.create(
            name="Committee room",
            description="",
            type=room_type,
            managed_by_group=cls.committee,
        )

    def reservation(self, reservable):
        start = timezone.now() + datetime.timedelta(days=2)
        return Reservation.objects.create(
            reservable=reservable,
            user=self.member,
            start=start,
            end=start + datetime.timedelta(hours=2),
        )

    def join(self, user, **dates):
        GroupMembership.objects.create(user=user, group=self.committee, **dates)


class EvaluatePermissionTestCase(ManagedReservablesTestCase):
    def test_unmanaged_is_evaluated_by_handlers(self):
        reservation = self.reservation(self.unmanaged)

        self.assertTrue(can_evaluate(self.handler, reservation))
        self.assertTrue(can_evaluate(self.superuser, reservation))
        self.assertFalse(can_evaluate(self.manager, reservation))
        self.assertFalse(can_evaluate(self.member, reservation))

    def test_managed_by_person_is_only_evaluated_by_them(self):
        reservation = self.reservation(self.by_person)

        self.assertTrue(can_evaluate(self.manager, reservation))
        self.assertFalse(can_evaluate(self.handler, reservation))
        self.assertFalse(can_evaluate(self.superuser, reservation))

    def test_managed_by_group_is_evaluated_by_active_members(self):
        reservation = self.reservation(self.by_group)
        former = make_user("former")
        future = make_user("future")
        today = timezone.localdate()
        self.join(self.member)
        self.join(former, member_until=today - datetime.timedelta(days=1))
        self.join(future, member_since=today + datetime.timedelta(days=1))

        self.assertTrue(can_evaluate(self.member, reservation))
        self.assertFalse(can_evaluate(former, reservation))
        self.assertFalse(can_evaluate(future, reservation))
        self.assertFalse(can_evaluate(self.handler, reservation))

    def test_discontinued_group_no_longer_manages(self):
        self.join(self.member)
        self.committee.date_discontinuation = timezone.localdate() - datetime.timedelta(
            days=1
        )
        self.committee.save()

        self.assertFalse(can_evaluate(self.member, self.reservation(self.by_group)))

    def test_manager_gets_admin_access_without_permissions(self):
        self.assertTrue(manages_reservables(self.manager))
        self.assertTrue(self.manager.is_staff)
        self.assertFalse(self.member.is_staff)

    def test_cannot_have_both_a_group_and_a_person_as_manager(self):
        self.by_person.managed_by_group = self.committee
        with self.assertRaises(IntegrityError):
            self.by_person.save()


class EvaluateInAdminTestCase(ManagedReservablesTestCase):
    def accept(self, user, reservation):
        self.client.force_login(user)
        url = reverse("admin:reservations_reservation_accept", args=[reservation.pk])
        return self.client.post(url)

    def test_manager_accepts_from_the_admin(self):
        reservation = self.reservation(self.by_person)

        response = self.accept(self.manager, reservation)

        self.assertEqual(response.status_code, 302)
        reservation.refresh_from_db()
        self.assertEqual(reservation.request_status, Reservation.RequestStatus.APPROVED)

    def test_handler_cannot_accept_a_managed_reservation(self):
        reservation = self.reservation(self.by_person)

        response = self.accept(self.handler, reservation)

        self.assertEqual(response.status_code, 403)
        reservation.refresh_from_db()
        self.assertEqual(reservation.request_status, Reservation.RequestStatus.PENDING)

    def test_accept_needs_a_post(self):
        reservation = self.reservation(self.by_person)
        self.client.force_login(self.manager)
        url = reverse("admin:reservations_reservation_accept", args=[reservation.pk])

        self.assertEqual(self.client.get(url).status_code, 405)

    def test_manager_only_lists_their_reservations(self):
        mine = self.reservation(self.by_person)
        other = self.reservation(self.unmanaged)
        self.client.force_login(self.manager)

        response = self.client.get(reverse("admin:reservations_reservation_changelist"))

        shown = list(response.context["cl"].result_list)
        self.assertIn(mine, shown)
        self.assertNotIn(other, shown)

    def test_handler_cannot_change_status_of_managed_reservation_in_form(self):
        reservation = self.reservation(self.by_person)
        self.client.force_login(self.handler)
        url = reverse("admin:reservations_reservation_change", args=[reservation.pk])

        form = self.client.get(url).context["adminform"].form

        self.assertNotIn("request_status", form.fields)


class HomeToDoTestCase(ManagedReservablesTestCase):
    def pending_on_home(self, user):
        self.client.force_login(user)
        return self.client.get(reverse("home:home")).context["pending_approvals"]

    def test_only_managers_get_the_to_do(self):
        reservation = self.reservation(self.by_person)

        self.assertEqual(self.pending_on_home(self.manager), [reservation])
        self.assertEqual(self.pending_on_home(self.handler), [])
        self.assertEqual(self.pending_on_home(self.superuser), [])

    def test_handlers_get_the_to_do_for_unmanaged(self):
        reservation = self.reservation(self.unmanaged)

        self.assertEqual(self.pending_on_home(self.handler), [reservation])
        self.assertEqual(self.pending_on_home(self.manager), [])
