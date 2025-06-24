"""Module defining the tests for the registration protocol."""

from datetime import datetime, timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G

from loefsys.events.models import Event, EventRegistration, RegistrationFormField
from loefsys.events.models.choices import EventCategories
from loefsys.events.models.registration import RegistrationStatus
from loefsys.events.models.registration_form_field import (
    BooleanRegistrationInformation,
    DatetimeRegistrationInformation,
    IntegerRegistrationInformation,
    TextRegistrationInformation,
)
from loefsys.users.models import User


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
        self.user2 = G(
            User,
            email="2@user.nl",
            password="secret1",
            phone_number="+31612345678",
            nickname="A",
            picture=None,
        )
        self.user3 = G(
            User,
            email="3@user.nl",
            password="secret1",
            phone_number="+31612345678",
            nickname="A",
            picture=None,
        )
        now = timezone.now()
        self.old_event = G(
            Event,
            title="Old event",
            description="Event from the past.",
            start=now - timedelta(weeks=10),
            end=now - timedelta(weeks=9),
            registration_start=now - timedelta(weeks=10, days=2),
            registration_deadline=now - timedelta(weeks=10, days=1),
            cancelation_deadline=now - timedelta(weeks=10, days=1),
            category=EventCategories.LEISURE,
            capacity=30,
            price=0.00,
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )
        self.upcoming_event = G(
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
        self.upcoming_event_with_form_fields = G(
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
        self.form_field_text = G(
            RegistrationFormField,
            event=self.upcoming_event_with_form_fields,
            type=RegistrationFormField.TEXT_FIELD,
            subject="Text",
            description="This is a text field.",
            required=False,
        )
        self.form_field_boolean = G(
            RegistrationFormField,
            event=self.upcoming_event_with_form_fields,
            type=RegistrationFormField.BOOLEAN_FIELD,
            subject="Boolean",
            description="This is a boolean field.",
            required=False,
        )
        self.form_field_integer = G(
            RegistrationFormField,
            event=self.upcoming_event_with_form_fields,
            type=RegistrationFormField.INTEGER_FIELD,
            subject="Integer",
            description="This is an integer field.",
            required=False,
        )
        self.form_field_datetime = G(
            RegistrationFormField,
            event=self.upcoming_event_with_form_fields,
            type=RegistrationFormField.DATETIME_FIELD,
            subject="Datetime",
            description="This is a datetime field.",
            required=False,
        )
        self.upcoming_event_with_required_form_fields = G(
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
        self.form_field_required_text = G(
            RegistrationFormField,
            event=self.upcoming_event_with_required_form_fields,
            type=RegistrationFormField.TEXT_FIELD,
            subject="Text",
            description="This is a required text field.",
            required=True,
        )
        self.upcoming_event_for_1_person = G(
            Event,
            title="Upcoming event for 1 person",
            description="Event for which 1 person can sign up.",
            start=now + timedelta(days=7),
            end=now + timedelta(days=8),
            registration_start=now - timedelta(days=1),
            registration_deadline=now + timedelta(days=6),
            cancelation_deadline=now + timedelta(days=6),
            category=EventCategories.LEISURE,
            capacity=1,
            price=0.00,
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )
        self.upcoming_event_with_early_cancellation_deadline = G(
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
            fine=0.00,
            location="The Netherlands",
            is_open_event=True,
            published=True,
            send_cancel_email=False,
        )

    def test_registration_upcoming(self):
        """Test for when a user registers for an event.

        When a user registers for an event, an event registration
        should be added to the database.
        """
        self.client.force_login(user=self.user1)

        # Test that at th is point no registrations exist
        self.assertTrue(self.upcoming_event.eventregistration_set.count() == 0)

        response = self.client.get(self.upcoming_event.get_absolute_url())
        self.assertNotContains(response=response, text="Je bent ingeschreven")

        # Test that after sending the POST request, the user has been registered
        response = self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )
        self.assertTrue(self.upcoming_event.eventregistration_set.count() == 1)
        self.assertTrue(self.upcoming_event.eventregistration_set.active().count() == 1)

        response = self.client.get(self.upcoming_event.get_absolute_url())
        self.assertContains(response=response, text="Je bent ingeschreven")

    def test_registration_form_simple(self):
        """Test for when a user registers for an event and fills in the form.

        When a user registers for an event, and fills in the form,
        an event registration should be added to the database and the form
        submission should be taken into account.
        """
        self.client.force_login(user=self.user1)

        self.assertTrue(
            self.upcoming_event_with_form_fields.eventregistration_set.count() == 0
        )

        response = self.client.get(
            self.upcoming_event_with_form_fields.get_absolute_url()
        )
        self.assertNotContains(response=response, text="Je bent ingeschreven")

        # Register for event
        response = self.client.post(
            reverse(
                "events:event", kwargs={"pk": self.upcoming_event_with_form_fields.pk}
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.assertEqual(
            response["Location"],
            reverse(
                "events:registration",
                kwargs={"slug": self.upcoming_event_with_form_fields.slug},
            ),
        )

        # Submit the event registration form
        text_field_pk = RegistrationFormField.objects.get(
            event=self.upcoming_event_with_form_fields,
            type=RegistrationFormField.TEXT_FIELD,
        ).pk
        boolean_field_pk = RegistrationFormField.objects.get(
            event=self.upcoming_event_with_form_fields,
            type=RegistrationFormField.BOOLEAN_FIELD,
        ).pk
        integer_field_pk = RegistrationFormField.objects.get(
            event=self.upcoming_event_with_form_fields,
            type=RegistrationFormField.INTEGER_FIELD,
        ).pk
        datetime_field_pk = RegistrationFormField.objects.get(
            event=self.upcoming_event_with_form_fields,
            type=RegistrationFormField.DATETIME_FIELD,
        ).pk
        response = self.client.post(
            reverse(
                "events:registration",
                kwargs={"slug": self.upcoming_event_with_form_fields.slug},
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                str(text_field_pk): "Hello",
                str(boolean_field_pk): "on",
                str(integer_field_pk): "3",
                str(datetime_field_pk): "2025-05-13T12:00",
            },
        )

        self.assertEqual(
            "Hello",
            TextRegistrationInformation.objects.filter(
                registration=EventRegistration.objects.filter(
                    event=self.upcoming_event_with_form_fields,
                    contact=self.user1,
                    status=RegistrationStatus.ACTIVE,
                ).first(),
                field=self.form_field_text,
            )
            .first()
            .value,
        )

        self.assertEqual(
            True,
            BooleanRegistrationInformation.objects.filter(
                registration=EventRegistration.objects.filter(
                    event=self.upcoming_event_with_form_fields,
                    contact=self.user1,
                    status=RegistrationStatus.ACTIVE,
                ).first(),
                field=self.form_field_boolean,
            )
            .first()
            .value,
        )

        self.assertEqual(
            3,
            IntegerRegistrationInformation.objects.filter(
                registration=EventRegistration.objects.filter(
                    event=self.upcoming_event_with_form_fields,
                    contact=self.user1,
                    status=RegistrationStatus.ACTIVE,
                ).first(),
                field=self.form_field_integer,
            )
            .first()
            .value,
        )

        self.assertEqual(
            timezone.make_aware(
                datetime.strptime("2025-05-13T12:00", "%Y-%m-%dT%H:%M")
            ),
            DatetimeRegistrationInformation.objects.filter(
                registration=EventRegistration.objects.filter(
                    event=self.upcoming_event_with_form_fields,
                    contact=self.user1,
                    status=RegistrationStatus.ACTIVE,
                ).first(),
                field=self.form_field_datetime,
            )
            .first()
            .value,
        )

        response = self.client.get(
            self.upcoming_event_with_form_fields.get_absolute_url()
        )
        self.assertContains(response=response, text="Je bent ingeschreven")

    def test_registration_form_required_fields_accept_complete(self):
        """Test for when a user registers and fills in the form with required fields.

        When a user registers for an event, and fills in the form with required fields,
        an event registration should be added to the database and the form
        submission should be taken into account.
        """
        self.client.force_login(user=self.user1)

        response = self.client.get(
            self.upcoming_event_with_required_form_fields.get_absolute_url()
        )
        self.assertNotContains(response=response, text="Je bent ingeschreven")

        # Register for event
        response = self.client.post(
            reverse(
                "events:event",
                kwargs={"pk": self.upcoming_event_with_required_form_fields.pk},
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        # Submit the event registration form
        required_text_field_pk = RegistrationFormField.objects.get(
            event=self.upcoming_event_with_required_form_fields,
            type=RegistrationFormField.TEXT_FIELD,
        ).pk
        response = self.client.post(
            reverse(
                "events:registration",
                kwargs={"slug": self.upcoming_event_with_required_form_fields.slug},
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                str(required_text_field_pk): "Hello",
            },
        )

        self.assertEqual(
            "Hello",
            TextRegistrationInformation.objects.filter(
                registration=EventRegistration.objects.filter(
                    event=self.upcoming_event_with_required_form_fields,
                    contact=self.user1,
                    status=RegistrationStatus.ACTIVE,
                ).first(),
                field=self.form_field_required_text,
            )
            .first()
            .value,
        )

        response = self.client.get(
            self.upcoming_event_with_required_form_fields.get_absolute_url()
        )
        self.assertContains(response=response, text="Je bent ingeschreven")

    def test_registration_form_required_fields_reject_incomplete(self):
        """Test for when a user registers and fills in the form with required fields.

        When a user registers for an event, and submits the form with required fields,
        without filling in the required fields (e.g. via a manual POST request),
        bypassing the client-side validation, then an event registration should still be
        added to the database but the form submission should not be taken into account.
        """
        self.client.force_login(user=self.user1)

        self.assertTrue(
            self.upcoming_event_with_required_form_fields.eventregistration_set.count()
            == 0
        )

        response = self.client.get(
            self.upcoming_event_with_required_form_fields.get_absolute_url()
        )
        self.assertNotContains(response=response, text="Je bent ingeschreven")

        # Register for event
        response = self.client.post(
            reverse(
                "events:event",
                kwargs={"pk": self.upcoming_event_with_required_form_fields.pk},
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        # Submit the event registration form
        required_text_field_pk = RegistrationFormField.objects.filter(
            event=self.upcoming_event_with_required_form_fields,
            type=RegistrationFormField.TEXT_FIELD,
        )
        response = self.client.post(
            reverse(
                "events:registration",
                kwargs={"slug": self.upcoming_event_with_required_form_fields.slug},
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                str(required_text_field_pk): "",
            },
        )

        self.assertTrue(TextRegistrationInformation.objects.all().count() == 0)

        response = self.client.get(
            self.upcoming_event_with_required_form_fields.get_absolute_url()
        )
        self.assertContains(response=response, text="Je bent ingeschreven")

    def test_reject_registration_old(self):
        """Test for when a user registers for an event that is not open anymore.

        When a user tries to register for an event of which the registration period has
        passed, nothing should happen.
        """
        self.client.force_login(user=self.user1)

        self.assertTrue(self.old_event.eventregistration_set.count() == 0)

        response = self.client.get(self.old_event.get_absolute_url())
        self.assertNotContains(response=response, text="Je bent ingeschreven")

        # Try to register for the event
        response = self.client.post(
            reverse("events:event", kwargs={"pk": self.old_event.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
            follow=True,
        )

        self.assertTrue(self.old_event.eventregistration_set.count() == 0)

    def test_cancellation_no_fine(self):
        """Test for when a user cancels their registration on time.

        When a user cancels their registration before the cancellation deadline,
        the status of their event registration should be set to cancelled (no fine).
        """
        self.client.force_login(user=self.user1)
        self.assertTrue(self.upcoming_event.eventregistration_set.count() == 0)

        # Set csrftoken cookie
        self.client.get(self.upcoming_event.get_absolute_url())

        # Register for the event
        self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.assertTrue(self.upcoming_event.eventregistration_set.count() == 1)

        # Cancel registration
        self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "cancel",
            },
        )

        self.assertTrue(
            self.upcoming_event.eventregistration_set.cancelled().first().status
            == RegistrationStatus.CANCELLED_NOFINE
        )

    def test_cancellation_fine_checkbox(self):
        """Test for when a user cancels their registration but not on time.

        When a user cancels their registration after the cancellation deadline with
        the fine checkbox checked on the cancellation form, the status of their event
        registration should be set to cancelled (fine).
        """
        self.client.force_login(user=self.user1)
        self.assertTrue(
            self.upcoming_event_with_early_cancellation_deadline.eventregistration_set.count()
            == 0
        )

        # Set csrftoken cookie
        self.client.get(
            self.upcoming_event_with_early_cancellation_deadline.get_absolute_url()
        )

        # Register for the event
        self.client.post(
            reverse(
                "events:event",
                kwargs={"pk": self.upcoming_event_with_early_cancellation_deadline.pk},
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.assertTrue(
            self.upcoming_event_with_early_cancellation_deadline.eventregistration_set.active().count()
            == 1
        )

        # Cancel registration with checkbox
        self.client.post(
            reverse(
                "events:event",
                kwargs={"pk": self.upcoming_event_with_early_cancellation_deadline.pk},
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "cancel",
                "fine-consent": "1",
            },
        )

        self.assertTrue(
            self.upcoming_event_with_early_cancellation_deadline.eventregistration_set.cancelled()
            .first()
            .status
            == RegistrationStatus.CANCELLED_FINE
        )

    def test_cancellation_fine_no_checkbox(self):
        """Test for when a user cancels their registration but not on time.

        When a user cancels their registration after the cancellation deadline with
        the fine checkbox NOT checked on the cancellation form, nothing about their
        event registration should change.
        """
        self.client.force_login(user=self.user1)

        self.assertTrue(
            self.upcoming_event_with_early_cancellation_deadline.eventregistration_set.count()
            == 0
        )

        # Set csrftoken cookie
        self.client.get(
            self.upcoming_event_with_early_cancellation_deadline.get_absolute_url()
        )

        # Register for the event
        self.client.post(
            reverse(
                "events:event",
                kwargs={"pk": self.upcoming_event_with_early_cancellation_deadline.pk},
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.assertTrue(
            self.upcoming_event_with_early_cancellation_deadline.eventregistration_set.active().count()
            == 1
        )

        # Cancel registration without checkbox
        self.client.post(
            reverse(
                "events:event",
                kwargs={"pk": self.upcoming_event_with_early_cancellation_deadline.pk},
            ),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "cancel",
            },
        )

        self.assertTrue(
            self.upcoming_event_with_early_cancellation_deadline.eventregistration_set.cancelled().count()
            == 0
        )

        self.assertTrue(
            self.upcoming_event_with_early_cancellation_deadline.eventregistration_set.active().count()
            == 1
        )

    def test_queue_simple(self):
        """Test for when a user registers when capacity has been reached.

        When a user registers for an event that is already full, the user should be
        added to the queue. Then when a user cancels their active registration,
        the status of their registration should be set to CANCELED and the person in
        the queue should be registered.
        """
        self.client.force_login(user=self.user1)
        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.count() == 0
        )

        # Set csrftoken cookie
        self.client.get(self.upcoming_event_for_1_person.get_absolute_url())

        # Register for the event (user1)
        self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event_for_1_person.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active().count() == 1
        )

        # Register for the event (user2)
        self.client.force_login(user=self.user2)

        # Set csrftoken cookie
        self.client.get(self.upcoming_event_for_1_person.get_absolute_url())

        self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event_for_1_person.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active().count() == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued().count() == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active()
            .first()
            .contact
            == self.user1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued()
            .first()
            .contact
            == self.user2
        )

        # Cancel registration (user1)
        self.client.force_login(user=self.user1)

        # Set csrftoken cookie
        self.client.get(self.upcoming_event_for_1_person.get_absolute_url())

        self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event_for_1_person.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "cancel",
            },
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active().count() == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued().count() == 0
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.cancelled().count()
            == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active()
            .first()
            .contact
            == self.user2
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.cancelled()
            .first()
            .contact
            == self.user1
        )

    def test_queue_precedence(self):
        """Test for when multiple users register for an already-full event.

        When a user with an active registration cancels their registration,
        the person that was added to the queue first should get registered.
        """
        # Register for the event (user1)
        self.client.force_login(user=self.user1)
        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.count() == 0
        )

        # Set csrftoken cookie
        self.client.get(self.upcoming_event_for_1_person.get_absolute_url())

        self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event_for_1_person.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active().count() == 1
        )

        # Register for the event (user2)
        self.client.force_login(user=self.user2)

        # Set csrftoken cookie
        self.client.get(self.upcoming_event_for_1_person.get_absolute_url())

        self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event_for_1_person.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active().count() == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued().count() == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active()
            .first()
            .contact
            == self.user1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued()
            .first()
            .contact
            == self.user2
        )

        # Register for the event (user3)
        self.client.force_login(user=self.user3)

        # Set csrftoken cookie
        self.client.get(self.upcoming_event_for_1_person.get_absolute_url())

        self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event_for_1_person.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "register",
            },
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active().count() == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued().count() == 2  # noqa: PLR2004
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active()
            .first()
            .contact
            == self.user1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued()
            .filter(contact=self.user2)
            .count()
            == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued()
            .filter(contact=self.user3)
            .count()
            == 1
        )

        # Cancel registration (user1)
        self.client.force_login(user=self.user1)

        # Set csrftoken cookie
        self.client.get(self.upcoming_event_for_1_person.get_absolute_url())

        self.client.post(
            reverse("events:event", kwargs={"pk": self.upcoming_event_for_1_person.pk}),
            data={
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "action": "cancel",
            },
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active().count() == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued().count() == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.cancelled().count()
            == 1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.active()
            .first()
            .contact
            == self.user2
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.cancelled()
            .first()
            .contact
            == self.user1
        )

        self.assertTrue(
            self.upcoming_event_for_1_person.eventregistration_set.queued()
            .first()
            .contact
            == self.user3
        )
