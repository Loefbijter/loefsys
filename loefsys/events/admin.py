"""
Admin configuration for the events module.

This module defines the admin interfaces for managing events and event registrations.
"""

from typing import ClassVar

from django.contrib import admin
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.translation import gettext_lazy as _

from loefsys.admin_helpers import ExportableModelAdmin

from .models import Event, EventOrganizer, EventRegistration
from .models.registration_form_field import (
    BooleanRegistrationInformation,
    DatetimeRegistrationInformation,
    IntegerRegistrationInformation,
    RegistrationFormField,
    TextRegistrationInformation,
)
from .permissions import allowed_categories


class RegistrationFormInline(admin.TabularInline):
    """Inline admin interface for registration form fields."""

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
    access to the rest of their member data.
    """

    model = EventRegistration
    fields = ("contact_name", "contact_email", "contact_phone", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = False
    verbose_name = _("Registration")
    verbose_name_plural = _("Registrations")

    def get_queryset(self, request):
        """Return the registrations with their contact fetched in the same query."""
        return super().get_queryset(request).select_related("contact")

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


class AbstractRegistrationInformationInline(admin.TabularInline):
    """Base class for registration information inline."""

    extra = 0
    can_delete = False
    fields = ("field", "value")
    readonly_fields = ("field",)

    def has_add_permission(self, request, obj=None):  # noqa ARG002
        """Make sure that admin cannot add new fields to an already submitted answer."""
        return False


class BooleanRegistrationInformationInline(AbstractRegistrationInformationInline):
    """Inline admin interface for registration information."""

    model = BooleanRegistrationInformation


class TextRegistrationInformationInline(AbstractRegistrationInformationInline):
    """Inline admin interface for registration information."""

    model = TextRegistrationInformation


class DatetimeRegistrationInformationInline(AbstractRegistrationInformationInline):
    """Inline admin interface for registration information."""

    model = DatetimeRegistrationInformation


class IntegerRegistrationInformationInline(AbstractRegistrationInformationInline):
    """Inline admin interface for registration information."""

    model = IntegerRegistrationInformation


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

    inlines = (
        BooleanRegistrationInformationInline,
        TextRegistrationInformationInline,
        IntegerRegistrationInformationInline,
        DatetimeRegistrationInformationInline,
    )


@admin.register(RegistrationFormField)
class RegistrationFormAdmin(ExportableModelAdmin):
    """Admin interface for managing registration form fields."""
