"""Admin configuration for the Reservation and Log models."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    ReservableBoat,
    ReservableMaterial,
    ReservableRoom,
    ReservableType,
    Reservation,
)

admin.site.register(ReservableType)
admin.site.register(ReservableBoat)
admin.site.register(ReservableMaterial)
admin.site.register(ReservableRoom)


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
        (_("Approval"), {"fields": ("status", "denial_reason")}),
    )

    def get_readonly_fields(self, request, obj=None):
        """Keep the reservation details editable on add, but lock them after creation."""
        if obj is None:
            return self.readonly_fields

        return (*self.readonly_fields, "reserved_item", "reservee_user", "start", "end")

    list_display = ("reservable", "user", "start", "end", "request_status")
    list_filter = ("request_status",)
    readonly_fields = ("created", "modified")
