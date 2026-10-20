from datetime import timedelta

from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import (
    Event,
    EventOrganizer,
    EventRegistration,
    RegistrationFormField,
)
from loefsys.events.models.choices import EventCategories
from loefsys.events.permissions import ACTIVITY_MANAGERS_GROUP, allowed_categories


def make_event(category, title):
    """Create an event with valid dates in the given category."""
    now = timezone.now()
    return G(
        Event,
        title=title,
        category=category,
        start=now + timedelta(days=7),
        end=now + timedelta(days=7, hours=2),
        registration_start=now - timedelta(days=1),
        registration_deadline=now + timedelta(days=6),
        cancelation_deadline=now + timedelta(days=6),
    )


class ActivityManagerAdminTestCase(TestCase):
    """Tests for activity managers restricted to some event categories."""

    def setUp(self):
        self.manager = G(get_user_model(), is_superuser=False)
        self.manager.groups.add(Group.objects.get(name=ACTIVITY_MANAGERS_GROUP))
        self.manager.user_permissions.add(
            Permission.objects.get(codename=EventCategories.LEISURE.permission_codename)
        )
        self.client.force_login(self.manager)

        self.leisure_event = make_event(EventCategories.LEISURE, "Borrel")
        self.sailing_event = make_event(EventCategories.SAILING, "Zeiltocht")
        self.attendee = G(
            get_user_model(),
            first_name="Testa",
            last_name="Deelnemer",
            email="deelnemer@example.com",
            phone_number="+31612345678",
            pod_kb_link="https://docs.google.com/spreadsheets/d/privatekb",
        )
        G(EventRegistration, event=self.leisure_event, contact=self.attendee)

    def test_preset_group_has_no_categories(self):
        """The preset group alone doesn't grant any category."""
        member = G(get_user_model(), is_superuser=False)
        member.groups.add(Group.objects.get(name=ACTIVITY_MANAGERS_GROUP))
        self.assertEqual(allowed_categories(member), [])

    def test_changelist_only_shows_allowed_categories(self):
        response = self.client.get(reverse("admin:events_event_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Borrel")
        self.assertNotContains(response, "Zeiltocht")

    def test_cannot_open_event_in_other_category(self):
        url = reverse("admin:events_event_change", args=[self.sailing_event.pk])
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_creator_becomes_organizer(self):
        """An event created in the admin lists its creator as an organizer."""
        event = make_event(EventCategories.LEISURE, "Nieuwe borrel")
        request = RequestFactory().post("/")
        request.user = self.manager
        model_admin = site._registry[Event]
        form = model_admin.get_form(request)(instance=event)
        setattr(form, "save_m2m", lambda: None)  # set by form.save(commit=False)
        model_admin.save_related(request, form, [], change=False)
        organizer = EventOrganizer.objects.get(event=event)
        self.assertQuerySetEqual(organizer.user.all(), [self.manager])

    def test_editing_doesnt_add_organizer(self):
        request = RequestFactory().post("/")
        request.user = self.manager
        model_admin = site._registry[Event]
        form = model_admin.get_form(request)(instance=self.leisure_event)
        setattr(form, "save_m2m", lambda: None)  # set by form.save(commit=False)
        model_admin.save_related(request, form, [], change=True)
        self.assertFalse(
            EventOrganizer.objects.filter(
                event=self.leisure_event, user=self.manager
            ).exists()
        )

    def test_category_choices_are_limited(self):
        response = self.client.get(reverse("admin:events_event_add"))
        self.assertEqual(response.status_code, 200)
        choices = [
            value
            for value, _label in response.context["adminform"]
            .form.fields["category"]
            .choices
            if value != ""
        ]
        self.assertEqual(choices, [EventCategories.LEISURE.value])

    def test_registrations_show_only_contact_details(self):
        url = reverse("admin:events_event_change", args=[self.leisure_event.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Testa Deelnemer")
        self.assertContains(response, "deelnemer@example.com")
        self.assertContains(response, "+31612345678")
        self.assertNotContains(response, "privatekb")
        self.assertNotContains(
            response, reverse("admin:members_user_change", args=[self.attendee.pk])
        )

    def test_registrations_fold_out_form_response(self):
        """Each registration row can be folded out to show the form answers."""
        field = G(
            RegistrationFormField,
            event=self.leisure_event,
            subject="Dieetwensen",
            type=RegistrationFormField.TEXT_FIELD,
        )
        registration = EventRegistration.objects.get(event=self.leisure_event)
        field.set_value_for(registration, "Geen pinda's")
        url = reverse("admin:events_event_change", args=[self.leisure_event.pk])
        response = self.client.get(url)
        self.assertContains(response, '<details class="form-response">')
        self.assertContains(response, ">Dieetwensen</dt>")
        self.assertContains(response, "Geen pinda&#x27;s")
        self.assertNotContains(response, "privatekb")

    def test_no_form_response_column_without_form(self):
        url = reverse("admin:events_event_change", args=[self.leisure_event.pk])
        response = self.client.get(url)
        self.assertNotContains(response, "form-response")

    def test_individual_organizers_hidden(self):
        """The organizer widget would list all members, so it is hidden."""
        url = reverse("admin:events_event_change", args=[self.leisure_event.pk])
        response = self.client.get(url)
        self.assertNotContains(response, 'name="eventorganizer-0-user"')

    def test_no_add_without_categories(self):
        self.manager.user_permissions.clear()
        response = self.client.get(reverse("admin:events_event_add"))
        self.assertEqual(response.status_code, 403)


class SuperuserEventAdminTestCase(TestCase):
    """Superusers keep access to every category."""

    def setUp(self):
        self.client.force_login(G(get_user_model(), is_superuser=True))

    def test_changelist_shows_all_categories(self):
        make_event(EventCategories.LEISURE, "Borrel")
        make_event(EventCategories.SAILING, "Zeiltocht")
        response = self.client.get(reverse("admin:events_event_changelist"))
        self.assertContains(response, "Borrel")
        self.assertContains(response, "Zeiltocht")


class RegistrationFormAdminTestCase(TestCase):
    """The form questions are edited on the event, not in an admin of their own."""

    def test_form_fields_have_no_admin_of_their_own(self):
        self.assertNotIn(RegistrationFormField, site._registry)

    def test_registration_admin_shows_form_response(self):
        self.client.force_login(G(get_user_model(), is_superuser=True))
        event = make_event(EventCategories.LEISURE, "Borrel")
        field = G(
            RegistrationFormField,
            event=event,
            subject="Kom je met de auto?",
            type=RegistrationFormField.BOOLEAN_FIELD,
        )
        registration = G(EventRegistration, event=event, contact=G(get_user_model()))
        field.set_value_for(registration, False)
        url = reverse("admin:events_eventregistration_change", args=[registration.pk])
        response = self.client.get(url)
        self.assertContains(response, '<details class="form-response" open>')
        self.assertContains(response, "Kom je met de auto?")
        self.assertContains(response, '<dd style="margin:0 0 0.5rem;">Nee</dd>')
