"""Admin configuration for the Reservation and Log models."""

from django.contrib import admin

from .models import ReservableBoat, ReservableMaterial, ReservableRoom, ReservableType

admin.site.register(ReservableType)
admin.site.register(ReservableBoat)
admin.site.register(ReservableMaterial)
admin.site.register(ReservableRoom)
