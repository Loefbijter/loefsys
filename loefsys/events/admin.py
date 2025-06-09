"""
Admin configuration for the events module.

This module defines the admin interfaces for managing events and event registrations.
"""

from typing import ClassVar

from django.contrib import admin

from .models import Event, EventOrganizer, EventRegistration
from .models.registration_form_field import (
    BooleanRegistrationInformation,
    DatetimeRegistrationInformation,
    IntegerRegistrationInformation,
    RegistrationFormField,
    TextRegistrationInformation,
)


class RegistrationFormInline(admin.TabularInline):
    """Inline admin interface for registration form fields."""

    model = RegistrationFormField
    extra = 0


class EventOrganizerInline(admin.TabularInline):
    """Inline admin interface for event organizers."""

    model = EventOrganizer
    filter_horizontal = ("groups", "user")
    extra = 1


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
class EventAdmin(admin.ModelAdmin):
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
        "capacity",
        "location",
        "category",
        "published",
    )
    inlines: ClassVar[list[type]] = [RegistrationFormInline, EventOrganizerInline]


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    """Admin interface for managing event registrations."""

    list_display = ("__str__", "status")

    inlines = (
        BooleanRegistrationInformationInline,
        TextRegistrationInformationInline,
        IntegerRegistrationInformationInline,
        DatetimeRegistrationInformationInline,
    )


@admin.register(RegistrationFormField)
class RegistrationFormAdmin(admin.ModelAdmin):
    """Admin interface for managing registration form fields."""
