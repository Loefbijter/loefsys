"""Module defining the tests or the event registration frontend."""

import io
import shutil
import tempfile
from datetime import timedelta

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event
from loefsys.events.models.choices import EventCategories
from loefsys.users.models import User


@override_settings(MEDIA_ROOT=lambda self: self.test_media_dir)
def generate_test_image_file(name="test.jpg", size=(100, 100), color=(255, 0, 0)):
    """Generate test image file."""
    file = io.BytesIO()
    image = Image.new("RGB", size, color)
    image.save(file, "JPEG")
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type="image/jpeg")


class EventHomepageTestCase(TestCase):
    """Tests for the homepage regarding events."""

    def setUp(self):
        """Set up users and events."""
        self.client = Client()
        self.test_media_dir = tempfile.mkdtemp()
        self.user1 = G(
            User,
            email="1@user.nl",
            password="secret1",
            phone_number="+31612345678",
            nickname="A",
            picture=None,
        )
        self.override = self.settings(MEDIA_ROOT=self.test_media_dir)
        self.override.enable()

    def tearDown(self):
        """Clean up method after tests are done."""
        shutil.rmtree(self.test_media_dir)

    def test_indexpage_event_picture(self):
        """Test if picture shows up correctly on index page."""
        now = timezone.now()
        event_with_picture = G(
            Event,
            title="Event with picture",
            description="Event with picture.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=now - timedelta(days=1),
            registration_deadline=now + timedelta(days=6),
            cancelation_deadline=now + timedelta(days=6),
            category=EventCategories.LEISURE,
            capacity=0,
            price=0.00,
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )
        event_with_picture.picture = generate_test_image_file()
        event_with_picture.save()

        self.client.force_login(user=self.user1)
        response = self.client.get("/")
        self.assertContains(
            response=response,
            text=f"/media/{event_with_picture.event_picture_upload_path(None)}",
        )

    def test_indexpage_event_no_picture(self):
        """Test if default picture shows up correctly on index page."""
        now = timezone.now()
        G(
            Event,
            title="Event without picture",
            description="Event without picture.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=now - timedelta(days=1),
            registration_deadline=now + timedelta(days=6),
            cancelation_deadline=now + timedelta(days=6),
            category=EventCategories.LEISURE,
            capacity=0,
            price=0.00,
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )

        self.client.force_login(user=self.user1)
        response = self.client.get("/")
        self.assertContains(response=response, text="/media/events/default.png")


class EventRegistrationTestCase(TestCase):
    """Tests for event registration."""

    def setUp(self):
        """Set up users and constants."""
        self.client = Client()
        self.user1 = G(
            User,
            email="1@user.nl",
            password="secret1",
            phone_number="+31612345678",
            nickname="A",
            picture=None,
        )
        now = timezone.now()
        self.event_with_capacity_0 = G(
            Event,
            title="Upcoming event",
            description="Event for which you can sign up right now.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=now - timedelta(days=1),
            registration_deadline=now + timedelta(days=6),
            cancelation_deadline=now + timedelta(days=6),
            category=EventCategories.LEISURE,
            capacity=0,
            price=0.00,
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )
        self.event_with_capacity_30 = G(
            Event,
            title="Upcoming event",
            description="Event for which you can sign up right now.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=now - timedelta(days=1),
            registration_deadline=now + timedelta(days=6),
            cancelation_deadline=now + timedelta(days=6),
            category=EventCategories.LEISURE,
            capacity=30,
            price=0.00,
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )
        self.event_with_capacity_none = G(
            Event,
            title="Upcoming event",
            description="Event for which you can sign up right now.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=now - timedelta(days=1),
            registration_deadline=now + timedelta(days=6),
            cancelation_deadline=now + timedelta(days=6),
            category=EventCategories.LEISURE,
            capacity=None,
            price=0.00,
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )
        self.event_with_10_euro_fine = G(
            Event,
            title="Upcoming event with early cancellation deadline",
            description="Event that has an early cancellation deadline.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=now - timedelta(days=2),
            registration_deadline=now + timedelta(days=6),
            cancelation_deadline=now - timedelta(days=1),
            category=EventCategories.LEISURE,
            capacity=30,
            price=0.00,
            fine=10.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )

    def test_number_of_registrations(self):
        """Test if number of registrations is displayed correctly."""
        self.client.force_login(user=self.user1)

        # Check number of registrations formatting
        response = self.client.get(self.event_with_capacity_30.get_absolute_url())
        self.assertContains(response=response, text="0 / 30")

        response = self.client.get(self.event_with_capacity_0.get_absolute_url())
        self.assertContains(response=response, text="0")

        response = self.client.get(self.event_with_capacity_none.get_absolute_url())
        self.assertContains(response=response, text="0")

        # Register for events
        self.client.post(
            reverse("events:event", kwargs={"pk": self.event_with_capacity_30.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.client.post(
            reverse("events:event", kwargs={"pk": self.event_with_capacity_0.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.client.post(
            reverse("events:event", kwargs={"pk": self.event_with_capacity_none.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        # Check number of registrations formatting
        response = self.client.get(self.event_with_capacity_30.get_absolute_url())
        self.assertContains(response=response, text="1 / 30")

        response = self.client.get(self.event_with_capacity_0.get_absolute_url())
        self.assertContains(response=response, text="1")

        response = self.client.get(self.event_with_capacity_none.get_absolute_url())
        self.assertContains(response=response, text="1")

    def test_cancellation_form_shows_fine_amount(self):
        """Test if the cancellation form shows the amount that's being fined."""
        self.client.force_login(user=self.user1)

        # Get csrf token
        self.client.get(self.event_with_10_euro_fine.get_absolute_url())

        # Register for event
        self.client.post(
            reverse("events:event", kwargs={"pk": self.event_with_10_euro_fine.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        # Check if fine amount is on cancellation form
        response = self.client.get(self.event_with_10_euro_fine.get_absolute_url())
        self.assertContains(response=response, text="(€10,00 boete)")
