from django.contrib import admin  # noqa: D100

from .models import Boat, Material, ReservableType, Reservation, Room


@admin.register(Boat, Material, Room, ReservableType, Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Admin interface for the boat, material, room, reservabletype and reservation."""
