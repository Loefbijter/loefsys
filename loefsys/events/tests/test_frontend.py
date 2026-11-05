"""Module defining the tests or the event registration frontend."""

from datetime import UTC, datetime, timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventRegistration
from loefsys.events.models.choices import EventCategories, RegistrationStatus
from loefsys.members.models import User


class EventHomepageTestCase(TestCase):
    """Tests for the homepage regarding events."""

    def setUp(self):
        """Set up a member and an upcoming event."""
        self.client = Client()
        self.user1 = G(User, email="1@user.nl", password="secret1", picture=None)
        now = timezone.now()
        self.event = G(
            Event,
            title="Klusdag",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            category=EventCategories.LEISURE,
            published=True,
        )
        self.client.force_login(user=self.user1)

    def test_next_registered_event_is_the_hero(self):
        """The next activity the member registered for is shown large at the top."""
        G(
            EventRegistration,
            event=self.event,
            contact=self.user1,
            status=RegistrationStatus.ACTIVE,
        )

        response = self.client.get("/")

        self.assertEqual(response.context["next_event"], self.event)
        self.assertNotIn(self.event, response.context["upcoming_events"])
        self.assertContains(response, 'class="hero')

    def test_unpublished_event_is_hidden_from_members(self):
        """A member doesn't see an event that isn't published yet."""
        self.event.published = False
        self.event.save()

        response = self.client.get("/")

        self.assertIsNone(response.context["next_event"])
        self.assertNotContains(response, "Klusdag")


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
            reverse("events:event", kwargs={"slug": self.event_with_capacity_30.slug}),
            data={"action": "register"},
        )

        self.client.post(
            reverse("events:event", kwargs={"slug": self.event_with_capacity_0.slug}),
            data={"action": "register"},
        )

        self.client.post(
            reverse(
                "events:event", kwargs={"slug": self.event_with_capacity_none.slug}
            ),
            data={"action": "register"},
        )

        # Check number of registrations formatting
        response = self.client.get(self.event_with_capacity_30.get_absolute_url())
        self.assertContains(response=response, text="1 / 30")

        response = self.client.get(self.event_with_capacity_0.get_absolute_url())
        self.assertContains(response=response, text="1")

        response = self.client.get(self.event_with_capacity_none.get_absolute_url())
        self.assertContains(response=response, text="1")

    def test_event_detail_shows_registration_button_without_picture(self):
        """Test that events without a picture still show the registration button."""
        self.client.force_login(user=self.user1)
        response = self.client.get(self.event_with_capacity_0.get_absolute_url())

        self.assertContains(response=response, text='<form method="post"', html=False)
        self.assertContains(
            response=response, text='name="action" value="register"', html=False
        )
        self.assertContains(
            response=response, text='id="registration-button"', html=False
        )

    def test_registration_button_is_enabled_when_registrations_open(self):
        """Test that the registration button is enabled while registrations are open."""
        self.client.force_login(user=self.user1)
        response = self.client.get(self.event_with_capacity_30.get_absolute_url())
        content = response.content.decode()

        self.assertRegex(
            content, r'<button[^>]*id="registration-button"[^>]*type="submit"[^>]*>'
        )
        self.assertNotRegex(
            content,
            r"<button[^>]*id=\"registration-button\"[^>]*\sdisabled(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?(?=\s|>)",
        )

    def test_registration_button_shows_disabled_reason_before_registration_start(self):
        """Test that users see why registration is disabled before it opens."""
        self.client.force_login(user=self.user1)
        now = timezone.now()
        future_event = G(
            Event,
            title="Future registration event",
            description="Event for which registration opens later.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=now + timedelta(days=1),
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
        response = self.client.get(future_event.get_absolute_url())
        content = response.content.decode()

        self.assertRegex(
            content,
            r"<button[^>]*id=\"registration-button\"[^>]*\sdisabled(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?(?=\s|>)",
        )
        self.assertRegex(content, r'title="Inschrijven vanaf [^"]+"')

    def test_registration_start_is_shown_in_local_time(self):
        """Test that the registration start in the button is in local time, not UTC."""
        self.client.force_login(user=self.user1)
        # 08:40 UTC is 10:40 in Europe/Amsterdam (CEST).
        registration_start = datetime(2099, 10, 20, 8, 40, tzinfo=UTC)
        future_event = G(
            Event,
            title="Future registration event",
            description="Event for which registration opens later.",
            start=registration_start + timedelta(days=7),
            end=registration_start + timedelta(days=8),
            registration_start=registration_start,
            registration_deadline=registration_start + timedelta(days=6),
            cancelation_deadline=registration_start + timedelta(days=6),
            category=EventCategories.LEISURE,
            capacity=30,
            price=0.00,
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )
        response = self.client.get(future_event.get_absolute_url())
        content = response.content.decode()

        self.assertRegex(content, r'title="Inschrijven vanaf [^"]*10:40[^"]*"')
        self.assertNotRegex(content, r'title="Inschrijven vanaf [^"]*08:40[^"]*"')

    def test_event_without_registration_start_allows_registration_until_deadline(self):
        """Test that events without an explicit registration start can still open."""
        self.client.force_login(user=self.user1)
        now = timezone.now()
        no_start_event = G(
            Event,
            title="No start event",
            description="Event without a registration start.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=None,
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
        response = self.client.get(no_start_event.get_absolute_url())
        content = response.content.decode()

        self.assertNotRegex(
            content,
            r"<button[^>]*id=\"registration-button\"[^>]*\sdisabled(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?(?=\s|>)",
        )
        self.assertRegex(
            content,
            r'<button[^>]*id="registration-button"[^>]*>\s*Inschrijven\s*</button>',
        )

    def test_event_detail_shows_cancel_action_when_registered(self):
        """Test that registered users are shown the cancel action."""
        self.client.force_login(user=self.user1)
        self.client.post(
            reverse("events:event", kwargs={"slug": self.event_with_capacity_0.slug}),
            data={"action": "register"},
        )
        response = self.client.get(self.event_with_capacity_0.get_absolute_url())

        content = response.content.decode()
        self.assertRegex(content, r'name="action" value="cancel"')
        self.assertRegex(
            content,
            r'<button[^>]*id="registration-button"[^>]*>\s*Afmelden\s*</button>',
        )

    def test_registered_user_can_deregister(self):
        """Test that registered users can deregister from the event."""
        self.client.force_login(user=self.user1)
        self.client.post(
            reverse("events:event", kwargs={"slug": self.event_with_capacity_30.slug}),
            data={"action": "register"},
        )
        self.client.post(
            reverse("events:event", kwargs={"slug": self.event_with_capacity_30.slug}),
            data={"action": "cancel"},
        )

        response = self.client.get(self.event_with_capacity_30.get_absolute_url())
        content = response.content.decode()

        self.assertRegex(content, r'name="action" value="register"')
        self.assertRegex(
            content,
            r'<button[^>]*id="registration-button"[^>]*>\s*Inschrijven\s*</button>',
        )

    def test_deregistering_event_without_cancelation_deadline(self):
        """Test deregistration works for events without a cancelation deadline."""
        self.client.force_login(user=self.user1)
        now = timezone.now()
        event_without_cancel_deadline = G(
            Event,
            title="Event without cancel deadline",
            description="Event without a cancelation deadline.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=now - timedelta(days=1),
            registration_deadline=now + timedelta(days=6),
            cancelation_deadline=None,
            category=EventCategories.LEISURE,
            capacity=30,
            price=0.00,
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )

        self.client.post(
            reverse(
                "events:event", kwargs={"slug": event_without_cancel_deadline.slug}
            ),
            data={"action": "register"},
        )
        response = self.client.post(
            reverse(
                "events:event", kwargs={"slug": event_without_cancel_deadline.slug}
            ),
            data={"action": "cancel"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertRegex(content, r'name="action" value="register"')
        self.assertRegex(
            content,
            r'<button[^>]*id="registration-button"[^>]*>\s*Inschrijven\s*</button>',
        )

    def test_cancellation_form_shows_fine_amount(self):
        """Test if the cancellation form shows the amount that's being fined."""
        self.client.force_login(user=self.user1)

        # Get csrf token
        self.client.get(self.event_with_10_euro_fine.get_absolute_url())

        # Register for event
        self.client.post(
            reverse("events:event", kwargs={"slug": self.event_with_10_euro_fine.slug}),
            data={"action": "register"},
        )

        # The cancel button and the consent to the fine name the amount
        response = self.client.get(self.event_with_10_euro_fine.get_absolute_url())
        self.assertContains(response=response, text="Afmelden (€ 10,00 boete)")
        self.assertContains(response=response, text="de boete van € 10,00")
