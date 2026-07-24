"""Admin configuration for the Reservation and Log models."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from loefsys.reservations.models.log import Log, Question
from loefsys.reservations.models.user_log import UserLog

from .models import Boat, Material, ReservableType, Reservation, Room


@admin.register(Boat, Material, Room, ReservableType)
class ReservableAdmin(admin.ModelAdmin):
    """Default admin interface for reservable models."""


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Admin interface for reservations."""

    list_display = (
        "reserved_item",
        "reservee_user",
        "start",
        "end",
        "status",
        "date_of_creation",
    )
    list_filter = (
        "status",
        "reserved_item__location",
        "reserved_item__reservable_type",
    )
    search_fields = (
        "reserved_item__name",
        "reservee_user__email",
        "reservee_user__first_name",
        "reservee_user__last_name",
    )
    ordering = ("-date_of_creation",)
    readonly_fields = ("date_of_creation",)
    fieldsets = (
        (
            _("Reservation details"),
            {
                "fields": (
                    "reserved_item",
                    "reservee_user",
                    "start",
                    "end",
                    "date_of_creation",
                )
            },
        ),
        (
            _("Approval"),
            {
                "fields": (
                    "status",
                    "denial_reason",
                )
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        """Keep the reservation details editable on add, but lock them after creation."""
        if obj is None:
            return self.readonly_fields

        return (
            *self.readonly_fields,
            "reserved_item",
            "reservee_user",
            "start",
            "end",
        )


class QuestionInline(admin.TabularInline):
    """Inline for questions."""

    model = Question
    extra = 1


class LogAdmin(admin.ModelAdmin):
    """Admin interface for creating a log."""

    inlines = (QuestionInline,)


admin.site.register(Log, LogAdmin)
admin.site.register(UserLog)
