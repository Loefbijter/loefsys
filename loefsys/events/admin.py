"""
Admin configuration for the events module.

This module defines the admin interfaces for managing events and event registrations.
"""

from typing import ClassVar

from django.contrib import admin
from django.db.models.fields import BLANK_CHOICE_DASH
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from loefsys.admin_helpers import ExportableModelAdmin

from .models import Event, EventOrganizer, EventRegistration, RegistrationFormField
from .models.registration import FORM_RESPONSE_PREFETCH
from .permissions import allowed_categories


def render_form_response(registration, *, open_=False):
    """Render the answers a registration gave to the event's registration form."""
    return render_to_string(
        "events/admin/form_response.html",
        {"answers": registration.form_fields, "open": open_},
    )


class RegistrationFormInline(admin.TabularInline):
    """Inline admin interface for the questions of an event's registration form."""

    model = RegistrationFormField
    extra = 0


class EventOrganizerInline(admin.TabularInline):
    """Inline admin interface for event organizers."""

    model = EventOrganizer
    filter_horizontal = ("groups", "user")
    extra = 1

    def get_fields(self, request, obj=None):
        """Hide the individual organizers from admins who can't view members.

        The widget for picking individual organizers lists every member, which
        activity managers are not supposed to see.
        """
        fields = super().get_fields(request, obj)
        if request.user.has_perm("members.view_user"):
            return fields
        return [field for field in fields if field != "user"]


class EventRegistrationInline(admin.TabularInline):
    """Read-only list of the people registered for an event.

    Only the name, email address and phone number of each registered person are
    shown, so that activity managers can contact participants without getting
    access to the rest of their member data. When the event has a registration
    form, each row can also be folded out to show the answers given.
    """

    model = EventRegistration
    fields = ("contact_name", "contact_email", "contact_phone", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = False
    verbose_name = _("Registration")
    verbose_name_plural = _("Registrations")

    def get_fields(self, request, obj=None):
        """Add the form response column for events with a registration form."""
        fields = super().get_fields(request, obj)
        if obj is not None and obj.has_form_fields:
            return [*fields, "form_response"]
        return fields

    def get_readonly_fields(self, request, obj=None):
        """Keep every column read-only, the form response included."""
        return self.get_fields(request, obj)

    def get_queryset(self, request):
        """Return the registrations with their contact and form answers."""
        return (
            super()
            .get_queryset(request)
            .select_related("contact", "event")
            .prefetch_related(*FORM_RESPONSE_PREFETCH)
        )

    def has_view_permission(self, request, obj=None):  # noqa: ARG002
        """Allow everyone who can view the event to see its registrations."""
        return request.user.has_perm("events.view_event") or request.user.has_perm(
            "events.change_event"
        )

    def has_add_permission(self, request, obj=None):  # noqa: ARG002
        """Registrations are made by members themselves, not in this inline."""
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ARG002
        """Keep the registration list read-only."""
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002
        """Keep the registration list read-only."""
        return False

    @admin.display(description=_("Name"))
    def contact_name(self, registration):
        """Return the full name of the registered person."""
        contact = registration.contact
        return f"{contact.first_name} {contact.last_name}".strip() if contact else "-"

    @admin.display(description=_("Email"))
    def contact_email(self, registration):
        """Return the email address of the registered person."""
        return registration.contact.email if registration.contact else "-"

    @admin.display(description=_("Phone number"))
    def contact_phone(self, registration):
        """Return the phone number of the registered person."""
        contact = registration.contact
        return str(contact.phone_number) if contact and contact.phone_number else "-"

    @admin.display(description=_("Form response"))
    def form_response(self, registration):
        """Return the answers to the registration form, folded away."""
        return render_form_response(registration)


@admin.register(Event)
class EventAdmin(ExportableModelAdmin):
    """Admin interface for the fields of the event class."""

    fields = (
        "title",
        "description",
        "picture",
        "start",
        "end",
        "registration_start",
        "registration_deadline",
        "cancelation_deadline",
        "price",
        "fine",
        "capacity",
        "location",
        "category",
        "published",
    )
    inlines: ClassVar[list[type]] = [
        RegistrationFormInline,
        EventOrganizerInline,
        EventRegistrationInline,
    ]

    def get_queryset(self, request):
        """Only show events in categories the user is allowed to manage."""
        return (
            super()
            .get_queryset(request)
            .filter(category__in=allowed_categories(request.user))
        )

    def has_add_permission(self, request):
        """Only allow adding events when the user may manage some category."""
        return super().has_add_permission(request) and bool(
            allowed_categories(request.user)
        )

    def has_change_permission(self, request, obj=None):
        """Only allow changing events in categories the user may manage."""
        return super().has_change_permission(request, obj) and (
            obj is None or obj.category in allowed_categories(request.user)
        )

    def has_delete_permission(self, request, obj=None):
        """Only allow deleting events in categories the user may manage."""
        return super().has_delete_permission(request, obj) and (
            obj is None or obj.category in allowed_categories(request.user)
        )

    def save_related(self, request, form, formsets, change):
        """Make whoever creates an event one of its organizers.

        Activity managers can't pick individual organizers, so without this an
        event they create wouldn't show up under their own events.
        """
        super().save_related(request, form, formsets, change)
        if not change:
            organizer, _created = EventOrganizer.objects.get_or_create(
                event=form.instance
            )
            organizer.user.add(request.user)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """Limit the category choices to the categories the user may manage."""
        if db_field.name == "category":
            allowed = allowed_categories(request.user)
            kwargs["choices"] = BLANK_CHOICE_DASH + [
                (category.value, category.label) for category in allowed
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(EventRegistration)
class EventRegistrationAdmin(ExportableModelAdmin):
    """Admin interface for managing event registrations."""

    list_display = ("__str__", "status")
    readonly_fields = ("form_response",)

    @admin.display(description=_("Form response"))
    def form_response(self, registration):
        """Return the answers this registration gave to the registration form."""
        return render_form_response(registration, open_=True)
