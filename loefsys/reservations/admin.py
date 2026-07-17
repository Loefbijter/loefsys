"""Admin configuration for the Reservation and Log models."""

from django.contrib import admin

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
    """Admin configuration for the Reservation model."""

    list_display = ("reservable", "user", "start", "end", "request_status")
    list_filter = ("request_status",)
    readonly_fields = ("created", "modified")
