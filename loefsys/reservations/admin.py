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


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Admin interface for reservations."""

    list_display = (
        "reservable",
        "user",
        "start",
        "end",
        "request_status",
        "date_of_creation",
    )
    list_filter = ("request_status", "reservable__location", "reservable__type")
    search_fields = (
        "reservable__name",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    ordering = ("-date_of_creation",)
    readonly_fields = ("date_of_creation",)
    fieldsets = (
        (
            _("Reservation details"),
            {"fields": ("reservable", "user", "start", "end", "date_of_creation")},
        ),
        (_("Approval"), {"fields": ("request_status", "status", "denial_reason")}),
    )

    def get_readonly_fields(self, _request, obj=None):
        """Keep the reservation details editable on add but lock them after creation."""
        if obj is None:
            return self.readonly_fields

        return (*self.readonly_fields, "reservable", "user", "start", "end")
