"""Tests for organizers adding members to an event."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventRegistration, RegistrationFormField
from loefsys.events.models.choices import EventCategories, RegistrationStatus
from loefsys.events.permissions import ACTIVITY_MANAGERS_GROUP

from .test_admin import make_event


def fmt(moment):
    """Format a datetime for the admin's split date and time widgets."""
    moment = timezone.localtime(moment)
    return {"0": moment.strftime("%Y-%m-%d"), "1": moment.strftime("%H:%M:%S")}


class AddRegistrationsMixin:
    """Helpers to drive the event admin with registrations to add."""

    def inline_data(self, response, members):
        """Build the inline formset data, adding ``members`` as new registrations.

        ``members`` is a list of dicts with the form data of each new registration.
        """
        data = {}
        for inline in response.context["inline_admin_formsets"]:
            formset = inline.formset
            prefix = formset.prefix
            adds = members if "prepaid" in formset.empty_form.fields else []
            data[f"{prefix}-TOTAL_FORMS"] = len(adds)
            data[f"{prefix}-INITIAL_FORMS"] = formset.initial_form_count()
            data[f"{prefix}-MIN_NUM_FORMS"] = 0
            data[f"{prefix}-MAX_NUM_FORMS"] = 1000
            for index, member in enumerate(adds):
                for key, value in member.items():
                    data[f"{prefix}-{index}-{key}"] = value
        return data

    def event_data(self, event):
        """Return the admin form data of an existing event."""
        data = {
            "title": event.title,
            "description": "",
            "location": event.location,
            "category": event.category,
            "capacity": event.capacity or "",
            "price": event.price,
            "fine": event.fine,
            "published": "on",
        }
        for field in ("start", "end", "registration_start", "registration_deadline"):
            for suffix, value in fmt(getattr(event, field)).items():
                data[f"{field}_{suffix}"] = value
        for suffix, value in fmt(event.cancelation_deadline).items():
            data[f"cancelation_deadline_{suffix}"] = value
        return data

    def add_members(self, event, *members):
        """Add members to an existing event through the admin change page."""
        url = reverse("admin:events_event_change", args=[event.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = self.event_data(event) | self.inline_data(
            response, [{"contact": member.pk} for member in members]
        )
        return self.client.post(url, data)


class OrganizerAddsRegistrationsTestCase(AddRegistrationsMixin, TestCase):
    """Superusers adding members to events through the event admin."""

    def setUp(self):
        self.admin = G(get_user_model(), is_superuser=True)
        self.client.force_login(self.admin)
        now = timezone.now()
        # Registration has not opened yet.
        self.event = G(
            Event,
            title="Kerstdiner",
            category=EventCategories.LEISURE,
            capacity=2,
            price=Decimal("25.00"),
            fine=Decimal("10.00"),
            start=now + timedelta(days=30),
            end=now + timedelta(days=30, hours=3),
            registration_start=now + timedelta(days=5),
            registration_deadline=now + timedelta(days=20),
            cancelation_deadline=now + timedelta(days=20),
            published=True,
        )
        self.members = [G(get_user_model()) for _ in range(3)]

    def test_added_member_is_active_before_registration_opens(self):
        response = self.add_members(self.event, self.members[0])
        self.assertEqual(response.status_code, 302)
        registration = EventRegistration.objects.get(contact=self.members[0])
        self.assertEqual(registration.status, RegistrationStatus.ACTIVE)
        self.assertTrue(registration.added_by_organizer)
        self.assertFalse(self.event.registrations_open())

    def test_added_members_stay_active_when_event_is_full(self):
        self.add_members(self.event, *self.members)
        statuses = EventRegistration.objects.filter(event=self.event).values_list(
            "status", flat=True
        )
        self.assertEqual(list(statuses), [RegistrationStatus.ACTIVE] * 3)
        self.assertTrue(self.event.max_capacity_reached())

    def test_regular_member_is_queued_behind_added_members(self):
        self.add_members(self.event, self.members[0], self.members[1])
        regular = EventRegistration(event=self.event, contact=self.members[2])
        regular.save()
        self.assertEqual(regular.status, RegistrationStatus.QUEUED)

    def test_added_members_leave_remaining_places_for_sign_ups(self):
        """With capacity 70 and 35 added members, 35 places stay open."""
        self.event.capacity = 70
        self.event.save()
        added = [G(get_user_model()) for _ in range(35)]
        self.add_members(self.event, *added)
        self.assertFalse(self.event.max_capacity_reached())
        for _ in range(35):
            registration = EventRegistration(
                event=self.event, contact=G(get_user_model())
            )
            registration.save()
            self.assertEqual(registration.status, RegistrationStatus.ACTIVE)
        late = EventRegistration(event=self.event, contact=G(get_user_model()))
        late.save()
        self.assertEqual(late.status, RegistrationStatus.QUEUED)

    def test_adding_members_never_moves_existing_registrations(self):
        """Earlier sign-ups keep their place, later ones go over capacity."""
        first, second, queued = (
            EventRegistration(event=self.event, contact=member)
            for member in self.members
        )
        first.save()
        second.save()
        queued.save()
        self.assertEqual(queued.status, RegistrationStatus.QUEUED)

        added = G(get_user_model())
        self.add_members(self.event, added)

        statuses = {
            registration.contact: registration.status
            for registration in EventRegistration.objects.filter(event=self.event)
        }
        self.assertEqual(statuses[self.members[0]], RegistrationStatus.ACTIVE)
        self.assertEqual(statuses[self.members[1]], RegistrationStatus.ACTIVE)
        self.assertEqual(statuses[self.members[2]], RegistrationStatus.QUEUED)
        self.assertEqual(statuses[added], RegistrationStatus.ACTIVE)
        self.assertEqual(self.event.eventregistration_set.active().count(), 3)

        # Over capacity (3/2): a cancellation doesn't promote anyone until the
        # number of active registrations drops below the capacity.
        first.cancel()
        queued.refresh_from_db()
        self.assertEqual(queued.status, RegistrationStatus.QUEUED)
        second.cancel()
        queued.refresh_from_db()
        self.assertEqual(queued.status, RegistrationStatus.ACTIVE)

    def test_price_is_copied_and_nothing_is_paid_by_default(self):
        self.add_members(self.event, self.members[0])
        registration = EventRegistration.objects.get(contact=self.members[0])
        self.assertEqual(registration.price_at_registration, Decimal("25.00"))
        self.assertEqual(registration.fine_at_registration, Decimal("10.00"))
        self.assertEqual(registration.costs_paid, Decimal("0.00"))
        self.assertEqual(registration.costs_to_pay(), Decimal("25.00"))

    def test_prepaid_member_owes_nothing(self):
        url = reverse("admin:events_event_change", args=[self.event.pk])
        response = self.client.get(url)
        data = self.event_data(self.event) | self.inline_data(
            response, [{"contact": self.members[0].pk, "prepaid": "on"}]
        )
        self.client.post(url, data)
        registration = EventRegistration.objects.get(contact=self.members[0])
        self.assertEqual(registration.costs_paid, Decimal("25.00"))
        self.assertEqual(registration.costs_to_pay(), Decimal("0.00"))

    def test_partial_payment_is_kept(self):
        url = reverse("admin:events_event_change", args=[self.event.pk])
        response = self.client.get(url)
        data = self.event_data(self.event) | self.inline_data(
            response, [{"contact": self.members[0].pk, "costs_paid": "10.00"}]
        )
        self.client.post(url, data)
        registration = EventRegistration.objects.get(contact=self.members[0])
        self.assertEqual(registration.costs_to_pay(), Decimal("15.00"))

    def test_member_cannot_be_added_twice(self):
        self.add_members(self.event, self.members[0])
        response = self.add_members(self.event, self.members[0])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["errors"])
        self.assertEqual(
            EventRegistration.objects.filter(contact=self.members[0]).count(), 1
        )

    def test_can_add_member_while_creating_event(self):
        url = reverse("admin:events_event_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = self.event_data(self.event) | self.inline_data(
            response, [{"contact": self.members[0].pk}]
        )
        data["title"] = "Nieuw diner"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302, getattr(response, "context", None))
        event = Event.objects.get(title="Nieuw diner")
        registration = EventRegistration.objects.get(event=event)
        self.assertEqual(registration.contact, self.members[0])
        self.assertEqual(registration.status, RegistrationStatus.ACTIVE)

    def test_added_member_appears_in_attendee_list(self):
        self.add_members(self.event, self.members[0])
        viewer = G(get_user_model())
        viewer.user_permissions.add(
            Permission.objects.get(codename="view_eventregistration")
        )
        self.client.force_login(viewer)
        response = self.client.get(self.event.get_absolute_url())
        self.assertEqual(
            [r.contact for r in response.context["attendees"]], [self.members[0]]
        )
        self.assertEqual(response.context["num_registrations"], 1)

    def test_cancelling_frees_a_place_for_the_queue(self):
        self.add_members(self.event, self.members[0], self.members[1])
        queued = EventRegistration(event=self.event, contact=self.members[2])
        queued.save()
        self.assertEqual(queued.status, RegistrationStatus.QUEUED)

        EventRegistration.objects.get(contact=self.members[0]).cancel()

        queued.refresh_from_db()
        self.assertEqual(queued.status, RegistrationStatus.ACTIVE)

    def test_cancelling_before_deadline_has_no_fine(self):
        self.add_members(self.event, self.members[0])
        registration = EventRegistration.objects.get(contact=self.members[0])
        registration.cancel()
        self.assertEqual(registration.status, RegistrationStatus.CANCELLED_NOFINE)

    def test_cancelling_after_deadline_has_fine(self):
        self.add_members(self.event, self.members[0])
        Event.objects.filter(pk=self.event.pk).update(
            cancelation_deadline=timezone.now() - timedelta(days=1),
            registration_start=timezone.now() - timedelta(days=3),
            registration_deadline=timezone.now() - timedelta(days=2),
        )
        registration = EventRegistration.objects.get(contact=self.members[0])
        registration.event.refresh_from_db()
        registration.cancel()
        registration.refresh_from_db()
        self.assertEqual(registration.status, RegistrationStatus.CANCELLED_FINE)
        self.assertEqual(registration.costs, Decimal("10.00"))


FILL_IN_BUTTON = (
    '<button type="button" class="btn btn-secondary" data-open-registration-modal'
)


class AddedMemberRegistrationFormTestCase(AddRegistrationsMixin, TestCase):
    """Added members still fill in the registration form themselves."""

    def setUp(self):
        self.event = make_event(EventCategories.LEISURE, "Borrel")
        self.event.published = True
        self.event.save()
        self.field = G(
            RegistrationFormField,
            event=self.event,
            subject="Dieetwensen",
            type=RegistrationFormField.TEXT_FIELD,
            required=False,
        )
        self.member = G(get_user_model())
        EventRegistration(
            event=self.event, contact=self.member, added_by_organizer=True
        ).save()
        self.client.force_login(self.member)

    def test_event_page_offers_the_form(self):
        response = self.client.get(self.event.get_absolute_url())
        self.assertContains(response, FILL_IN_BUTTON)

    def test_filling_in_the_form_keeps_the_added_registration(self):
        response = self.client.post(
            reverse("events:registration", kwargs={"slug": self.event.slug}),
            {str(self.field.pk): "Vegetarisch"},
        )
        self.assertEqual(response.status_code, 302)
        registration = EventRegistration.objects.get(event=self.event)
        self.assertTrue(registration.added_by_organizer)
        self.assertEqual(self.field.get_value_for(registration), "Vegetarisch")

    def test_regular_member_gets_no_extra_button(self):
        other = G(get_user_model())
        EventRegistration(event=self.event, contact=other).save()
        self.client.force_login(other)
        response = self.client.get(self.event.get_absolute_url())
        self.assertNotContains(response, FILL_IN_BUTTON)


class ActivityManagerAddsRegistrationsTestCase(AddRegistrationsMixin, TestCase):
    """Activity managers may only add members to events in their categories."""

    def setUp(self):
        self.manager = G(get_user_model(), is_superuser=False)
        self.manager.groups.add(Group.objects.get(name=ACTIVITY_MANAGERS_GROUP))
        self.manager.user_permissions.add(
            Permission.objects.get(codename=EventCategories.LEISURE.permission_codename)
        )
        self.client.force_login(self.manager)
        self.leisure_event = make_event(EventCategories.LEISURE, "Borrel")
        self.sailing_event = make_event(EventCategories.SAILING, "Zeiltocht")
        self.member = G(get_user_model())

    def test_preset_group_may_add_registrations(self):
        self.assertTrue(self.manager.has_perm("events.add_eventregistration"))

    def test_manager_can_add_member_to_own_category(self):
        response = self.add_members(self.leisure_event, self.member)
        self.assertEqual(response.status_code, 302)
        registration = EventRegistration.objects.get(event=self.leisure_event)
        self.assertEqual(registration.contact, self.member)
        self.assertEqual(registration.status, RegistrationStatus.ACTIVE)

    def test_manager_cannot_reach_event_in_other_category(self):
        url = reverse("admin:events_event_change", args=[self.sailing_event.pk])
        self.assertNotEqual(self.client.get(url).status_code, 200)
        data = self.event_data(self.sailing_event) | {
            "eventregistration_set-TOTAL_FORMS": 1,
            "eventregistration_set-INITIAL_FORMS": 0,
            "eventregistration_set-0-contact": self.member.pk,
        }
        self.client.post(url, data)
        self.assertFalse(
            EventRegistration.objects.filter(event=self.sailing_event).exists()
        )

    def test_manager_without_permission_gets_no_form(self):
        self.manager.groups.clear()
        self.manager.user_permissions.add(
            *Permission.objects.filter(
                codename__in=("add_event", "change_event", "view_event")
            )
        )
        response = self.client.get(
            reverse("admin:events_event_change", args=[self.leisure_event.pk])
        )
        self.assertEqual(response.status_code, 200)
        names = [
            inline.opts.__class__.__name__
            for inline in response.context["inline_admin_formsets"]
        ]
        self.assertNotIn("AddRegistrationInline", names)
