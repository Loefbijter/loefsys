"""Module defining the class-based views for the reservations."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from loefsys.reservations.models.reservation import Reservation


class ReservationCreateView(LoginRequiredMixin, CreateView):
    """Reservation create view."""

    model = Reservation
    fields = ("reserved_item", "start", "end")


class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    """Reservation update view."""

    model = Reservation
    fields = ("reserved_item", "start", "end")


class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    """Reservation delete view."""

    model = Reservation


class ReservationDetailView(LoginRequiredMixin, DetailView):
    """Reservation detail view."""

    model = Reservation
