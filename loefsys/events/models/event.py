"""In this module, the models for events are defined."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import validators
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import CheckConstraint, F, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleSlugDescriptionModel

from loefsys.events.models.choices import EventCategories, RegistrationStatus
from loefsys.events.models.managers import EventManager, EventRegistrationManager
from loefsys.groups.models import LoefbijterGroup


class OverwriteStorage(FileSystemStorage):
    """Custom storage class that overwrites files with the same name.

    Needed because when a user uploads a new profile picture, the old
    one would otherwise still be present together with the new one that
    gets renamed.
    """

    def get_available_name(self, name, max_length=None):  # noqa: ARG002
        """Given the desired name, derive and return a name that is available."""
        if self.exists(name):
            self.delete(name)
        return name


class Event(TitleSlugDescriptionModel, TimeStampedModel):
    """Model for an event.

    An event is an activity that people can sign up for. This can be a
    sail training, a cantus, or any other activity that is organized for
    the association. Events have many properties, such as a start and end date,
    a category, a price, a location, and more.

    Attributes
    ----------
    created : ~datetime.datetime
        The timestamp of the creation of the model, automatically generated upon
        creation.
    modified : ~datetime.datetime
        The timestamp of last modification of this model, automatically generated upon
        update.
    title : str
        The title to display for the event.
    description : str, None
        An optional description of the event.
    picture : ~django.db.models.fields.files.ImageFieldFile
        The picture for an event.
    slug : str
        A slug for the URL of the event, automatically generated from the title.
    start : ~datetime.datetime
        The start date and time of the event.
    end : ~datetime.datetime
        The end date and time of the event.
    registration_start : ~datetime.datetime
        The start date and time of the registration window
    registration_deadline : ~datetime.datetime
        The end date and time of the registration window
    cancelation_deadline : ~datetime.datetime
        The end date and time of the cancelation window
    category : ~loefsys.events.models.choices.EventCategories
        The category of the event.
    capacity : ~integer.Integer
        The maximum number of participants if there is one
    price : ~decimal.Decimal
        The price.
    fine : ~decimal.Decimal
        The fine if a participant does not show up.
    location : str
        The location of the event.

        We might want to include a Google Maps widget showing the location.
        `django-google-maps <https://pypi.org/project/django-google-maps/>`_ might be
        useful for this.
    is_open_event : bool
        Flag to determine if non-members can register.
    published : bool
        Flag to determine if the event is publicly visible.
    send_cancel_email : ~bool
        Flag to determine if an email should be sent if a participant deregisters
    eventregistration_set : ~loefsys.events.models.managers.EventRegistrationManager
        A manager of registrations for this event.

        It is the one-to-many relationship to
        :class:`~loefsys.events.models.EventRegistration`.
    """

    def event_picture_upload_path(self, _):
        """Return the upload path for the event picture."""
        return f"events/{self.slug}/picture.jpg"

    picture = models.ImageField(
        upload_to=event_picture_upload_path,
        null=True,
        blank=True,
        storage=OverwriteStorage(),
    )

    start = models.DateTimeField(_("Start time"))
    end = models.DateTimeField(_("End time"))

    registration_start = models.DateTimeField(
        _("Start of registration window"), blank=True, null=True
    )

    registration_deadline = models.DateTimeField(
        _("Registration deadline"), blank=True, null=True
    )
    cancelation_deadline = models.DateTimeField(
        _("Cancelation deadline"), blank=True, null=True
    )

    category = models.PositiveSmallIntegerField(
        choices=EventCategories, verbose_name=_("Category")
    )

    capacity = models.PositiveSmallIntegerField(
        _("Maximum number of participants"), blank=True, null=True
    )

    price = models.DecimalField(
        _("Price"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        blank=True,
        validators=[validators.MinValueValidator(0)],
    )
    fine = models.DecimalField(
        _("Fine"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        blank=True,
        help_text=_("Fine if participant does not show up."),
        validators=[validators.MinValueValidator(0)],
    )

    location = models.CharField(_("Location"), max_length=255)

    is_open_event = models.BooleanField(
        help_text=_("Event is open for non-members"), default=False
    )
    published = models.BooleanField(_("Published"), default=False)

    send_cancel_email = models.BooleanField(
        _("Send cancellation notifications"),
        default=True,
        help_text=_(
            "Send an email to the organising party when a member "
            "cancels their registration after the deadline."
        ),
    )

    @property
    def has_form_fields(self) -> bool:
        """Check if the event has associated form fields.

        Returns
        -------
        bool
            ``True`` if the event has form fields, otherwise ``False``.
        """
        return self.registrationformfield_set.count() > 0

    eventregistration_set: EventRegistrationManager

    objects = EventManager()

    class Meta:
        constraints = (
            CheckConstraint(
                condition=Q(end__gt=F("start")),
                name="event_end_gt_start",
                violation_error_message="End time cannot be before the start time.",
            ),
            CheckConstraint(
                condition=Q(start__gt=F("registration_deadline")),
                name="event_start_gt_reg_end",
                violation_error_message="registration deadline can't be after start.",
            ),
            CheckConstraint(
                condition=Q(start__gt=F("cancelation_deadline")),
                name="event_start_gt_can_end",
                violation_error_message="cancelation deadline can't be after start.",
            ),
            CheckConstraint(
                condition=Q(registration_deadline__gt=F("registration_start")),
                name="reg_end_gt_reg_start",
                violation_error_message="start of registration can't be after the end.",
            ),
            CheckConstraint(
                condition=Q(cancelation_deadline__gt=F("registration_start")),
                name="can_end_gt_reg_start",
                violation_error_message="cancelation can't be before registration opens",  # noqa: E501
            ),
        )

    def __str__(self):
        return f"{self.title}"

    @property
    def url(self) -> str:
        """Url for the event."""
        return self.get_absolute_url()

    def get_absolute_url(self):
        """Return the detail page url for this registration."""
        return reverse("events:event", kwargs={"slug": self.slug})

    def mandatory_registration(self) -> bool:
        """Check whether this event has mandatory registration.

        Returns
        -------
        bool
            A boolean that defines whether registration is mandatory.
        """
        return self.capacity is not None and self.capacity > 0

    def registrations_open(self) -> bool:
        """Determine whether it is possible for users to register for this event.

        Returns
        -------
        bool
            A boolean that defines whether registrations are open.
        """
        if not self.published or not self.registration_deadline:
            return False
        return self.registration_start < timezone.now() < self.registration_deadline

    def max_capacity_reached(self) -> bool:
        """Check whether the max capacity for this event is reached.

        Returns
        -------
        bool
            ``True`` when the event is full and ``False`` if there are places available.
        """
        return (
            self.capacity is not None
            and self.capacity <= self.eventregistration_set.active().count()
        )

    def fine_on_cancellation(self) -> bool:
        """Check whether the cancellation of a registration will result in a fine.

        Returns
        -------
        bool
            ``True`` when a fine will be applied and ``False`` when cancellation is
            free of charge.
        """
        if not self.mandatory_registration():
            return True
        deadline = self.cancelation_deadline or self.start
        return deadline < timezone.now()

    def process_cancellation(self) -> None:
        """Process the side effects for an event of a cancellation.

        Returns
        -------
        None
        """
        if not self.mandatory_registration():
            return

        num_active = self.eventregistration_set.active().count()
        num_queued = self.eventregistration_set.queued().count()
        if not num_queued or num_active >= self.capacity:
            return

        num_available = self.capacity - num_active
        num_to_add = min(num_available, num_queued)
        objs = self.eventregistration_set.queued().order_by("created")[:num_to_add]
        modified = timezone.now()
        for obj in objs:
            obj.status = RegistrationStatus.ACTIVE
            obj.modified = modified
        # As save() isn't called on the objects, we manually update the field modified.
        self.eventregistration_set.bulk_update(objs, ["status", "modified"])

    def registration_window_open(self) -> bool:
        """Determine whether it is possible for users to register for this event.

        For events with required registration, registration is only possible when the
        event is published and in the registration window defined by
        :attr:`.start` and :attr:`.end`.

        Returns
        -------
        bool
            A boolean that defines whether registrations are in the registration window.
        """
        return self.start < timezone.now() < self.end


class EventOrganizer(TimeStampedModel):
    """Utility model collecting the organizers for an event.

    Attributes
    ----------
    created : ~datetime.datetime
        The timestamp of the creation of the model, automatically generated upon
        creation.
    modified : ~datetime.datetime
        The timestamp of last modification of this model, automatically generated upon
        update.
    event : ~loefsys.events.models.event.Event
        The event that the current organizer organizes.
    groups : ~django.db.models.query.QuerySet of ~loefsys.groups.models.LoefbijterGroup
        The groups organizing this event.
    user : ~django.db.models.query.QuerySet of ~loefsys.users.models.User
        Individuals organizing this event.
    """

    event = models.OneToOneField(
        Event, on_delete=models.CASCADE, verbose_name=_("Event")
    )

    groups = models.ManyToManyField(
        to=LoefbijterGroup, related_name="organizing_group", blank=True
    )

    user = models.ManyToManyField(
        to=get_user_model(), related_name="organizer", blank=True
    )
