import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventOrganizer, EventRegistration
from loefsys.events.models.choices import EventCategories, RegistrationStatus


class EventDetailAttendeesTestCase(TestCase):
    """Tests for the attendee grid on the event detail page."""

    def setUp(self):
        now = timezone.now()
        self.event = G(
            Event,
            start=now + timezone.timedelta(days=7),
            end=now + timezone.timedelta(days=7, hours=2),
            registration_start=now - timezone.timedelta(days=1),
            registration_deadline=now + timezone.timedelta(days=6),
            cancelation_deadline=now + timezone.timedelta(days=6),
            published=True,
        )
        self.attendee = G(get_user_model())
        G(EventRegistration, event=self.event, contact=self.attendee)
        self.viewer = G(get_user_model())
        self.client.force_login(self.viewer)

    def test_attendees_hidden_without_permission(self):
        """Attendee grid should not render without the view_eventregistration perm."""
        response = self.client.get(self.event.get_absolute_url())
        self.assertFalse(response.context["can_view_attendees"])

    def test_attendees_visible_with_permission(self):
        """Attendee grid renders for users with the view_eventregistration perm."""
        perm = Permission.objects.get(codename="view_eventregistration")
        self.viewer.user_permissions.add(perm)
        response = self.client.get(self.event.get_absolute_url())
        self.assertTrue(response.context["can_view_attendees"])
        self.assertIn(self.attendee, [r.contact for r in response.context["attendees"]])


class EventFillerViewTestCase(TestCase):
    """Tests for the event filler JSON endpoint."""

    def setUp(self):
        self.client.force_login(G(get_user_model()))

    def test_event_filler_includes_picture_url(self):
        """The event filler should expose event pictures for calendar rendering."""
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root, MEDIA_URL="/media/"):
                event = G(
                    Event,
                    title="Evenement met foto",
                    start=timezone.now() + timezone.timedelta(days=7),
                    end=timezone.now() + timezone.timedelta(days=8),
                    registration_start=timezone.now() - timezone.timedelta(days=1),
                    registration_deadline=timezone.now() + timezone.timedelta(days=6),
                    cancelation_deadline=timezone.now() + timezone.timedelta(days=6),
                    category=1,
                    capacity=10,
                    price=0.00,
                    fine=0.00,
                    location="Nederland",
                    is_open_event=True,
                    published=True,
                    send_cancel_email=False,
                )
                event.picture = SimpleUploadedFile(
                    "test.jpg",
                    b"\xff\xd8\xff\xe0" + b"0" * 1024,
                    content_type="image/jpeg",
                )
                event.save()

                response = self.client.get(reverse("events:event_filler"))
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]["picture_url"], event.picture.url)
                self.assertEqual(data[0]["url"], event.get_absolute_url())

    def test_event_detail_shows_description_and_fine_consent_checkbox(self):
        """Event detail should display description and fine consent."""
        user = G(get_user_model())
        event = G(
            Event,
            title="Evenement met boete",
            description="Dit is het evenementbeschrijving.",
            start=timezone.now() + timezone.timedelta(days=7),
            end=timezone.now() + timezone.timedelta(days=7, hours=2),
            registration_start=timezone.now() - timezone.timedelta(days=7),
            registration_deadline=timezone.now() + timezone.timedelta(days=2),
            cancelation_deadline=timezone.now() - timezone.timedelta(days=1),
            category=1,
            capacity=10,
            price=10.00,
            fine=5.00,
            location="Nederland",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )
        G(
            EventRegistration,
            event=event,
            contact=user,
            status=RegistrationStatus.ACTIVE,
        )
        self.client.force_login(user)

        response = self.client.get(event.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, event.description)
        self.assertContains(response, 'name="fine-consent"')
        self.assertContains(response, "Afmelden (met boete)")


class MyEventsFeatureTestCase(TestCase):
    """Tests for the organizer event list and detail pages."""

    def setUp(self):
        self.organizer = G(get_user_model())
        self.attendee = G(
            get_user_model(),
            first_name="Test",
            last_name="Attendee",
            email="attendee@example.com",
            phone_number="+31612345678",
            pod_kb_link="https://docs.google.com/spreadsheets/d/testkb",
            pod_zb_link="https://docs.google.com/spreadsheets/d/testzb",
        )
        now = timezone.now()
        self.event = G(
            Event,
            title="Training Event",
            start=now + timezone.timedelta(days=7),
            end=now + timezone.timedelta(days=8),
            registration_start=now - timezone.timedelta(days=1),
            registration_deadline=now + timezone.timedelta(days=6),
            cancelation_deadline=now + timezone.timedelta(days=6),
            category=EventCategories.TRAINING,
            capacity=10,
            price=0.00,
            fine=0.00,
            location="Nederland",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )
        self.event_organizer = G(EventOrganizer, event=self.event)
        self.event_organizer.user.add(self.organizer)
        G(EventRegistration, event=self.event, contact=self.attendee)
        self.client.force_login(self.organizer)

    def test_menu_shows_mijn_events_for_organizer(self):
        response = self.client.get("/")
        self.assertContains(response, "Mijn events")
        self.assertContains(response, reverse("events:my_events"))

    def test_my_events_list_shows_organized_events(self):
        response = self.client.get(reverse("events:my_events"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)
        self.assertContains(
            response,
            reverse("events:my_events_event", kwargs={"slug": self.event.slug}),
        )

    def test_organized_event_detail_shows_attendee_profiles_and_training_data(self):
        response = self.client.get(
            reverse("events:my_events_event", kwargs={"slug": self.event.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)
        self.assertContains(response, self.event.get_absolute_url())
        self.assertContains(response, self.attendee.display_name)
        self.assertContains(
            response, reverse("members:profile", kwargs={"slug": self.attendee.slug})
        )
        self.assertContains(response, self.attendee.phone_number)
        self.assertContains(response, self.attendee.pod_kb_link)
        self.assertContains(response, self.attendee.pod_zb_link)

    def test_non_organizer_cannot_access_organized_event_detail(self):
        other_user = G(get_user_model())
        self.client.force_login(other_user)
        response = self.client.get(
            reverse("events:my_events_event", kwargs={"slug": self.event.slug})
        )
        self.assertEqual(response.status_code, 404)
