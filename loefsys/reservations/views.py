"""Module defining the class-based views for the reservations."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView

from loefsys.reservations.forms import (
    BoatLogbookForm,
    CreateReservationForm,
    SortByReservationForm,
)
from loefsys.reservations.models.boat import ReservableBoat
from loefsys.reservations.models.logbook import BoatDamageRecord, BoatLogbook
from loefsys.reservations.models.reservable import Reservable, ReservableType
from loefsys.reservations.models.reservation import Reservation


class ReservationListView(LoginRequiredMixin, ListView):
    """Reservation list view."""

    model = Reservation
    context_object_name = "reservations"

    def get_queryset(self):
        """Only show instances of Reservation made by the user, with the option to sort them."""  # noqa: E501
        form = SortByReservationForm(self.request.GET)
        sort_by = "start"

        if form.is_valid() and form.cleaned_data["sort_by"]:
            match form.cleaned_data["sort_by"]:
                case "location":
                    sort_by = "reservable__location"
                case "A-Z":
                    sort_by = Lower("reservable__name")
                case "type":
                    sort_by = "reservable__type__name"
                case _:
                    sort_by = form.cleaned_data["sort_by"]

        now = timezone.now()
        queryset = (
            Reservation.objects.filter(user=self.request.user)
            .exclude(request_status=Reservation.RequestStatus.DENIED)
            .order_by(sort_by)
        )

        queryset = queryset.filter(
            Q(end__gt=now)
            | (
                Q(reservable__type__category=ReservableType.Category.BOAT)
                & Q(end__lt=now)
                & Q(boat_logbook__isnull=True)
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        """Include the sort form in the context data."""
        context = super().get_context_data(**kwargs)
        context["form"] = SortByReservationForm(self.request.GET)
        context["RequestStatus"] = Reservation.RequestStatus
        return context


class ReservationCreateView(LoginRequiredMixin, CreateView):
    """Reservation create view."""

    model = Reservation
    form_class = CreateReservationForm
    success_url = reverse_lazy("reservations:reservations")

    def get_form(self, *args, **kwargs):
        """Include the location in the form."""
        form = super().get_form(*args, **kwargs)

        form.fields["reservable"].queryset = Reservable.objects.filter(
            location=self.kwargs.get("location")
        ).order_by("-is_reservable")

        reservable_type = ReservableType.objects.filter(
            name=self.request.GET.get("reservable_type")
        ).first()
        if reservable_type:
            form.fields["reservable"].queryset = Reservable.objects.filter(
                location=self.kwargs.get("location"), type=reservable_type
            ).order_by("-is_reservable")

        return form

    def form_valid(self, form):
        """Add the user who made the reservation to the Reservation instance."""
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Include the location and available type filters in the context data."""
        context = super().get_context_data(**kwargs)
        location = self.kwargs.get("location")
        context["location"] = location
        context["selected_reservable_type"] = self.request.GET.get("reservable_type")
        context["reservable_types"] = (
            ReservableType.objects.filter(reservable__location=location)
            .distinct()
            .order_by("name")
        )
        return context

    @staticmethod
    def check_availability(request):
        """Check if an item is available during the given timeslot."""
        start = request.GET.get("start")
        end = request.GET.get("end")
        reservable_id = request.GET.get("reservable")

        if start < end:
            conflicts = Reservation.objects.filter(reservable_id=reservable_id).filter(
                Q(start__range=(start, end))
                | Q(end__range=(start, end))
                | Q(start__lt=start, end__gt=end)
            )
            available = not conflicts.exists()
        else:
            available = False

        return JsonResponse({"available": available})


class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    """Reservation update view."""

    model = Reservation
    form_class = CreateReservationForm
    success_url = reverse_lazy("reservations:reservations")

    def get_form(self, *args, **kwargs):
        """Include the location in the form."""
        form = super().get_form(*args, **kwargs)

        form.fields["reservable"].queryset = Reservable.objects.filter(
            location=self.kwargs.get("location")
        ).order_by("-is_reservable")

        reservable_type = ReservableType.objects.filter(
            name=self.request.GET.get("reservable_type")
        ).first()
        if reservable_type:
            form.fields["reservable"].queryset = Reservable.objects.filter(
                location=self.kwargs.get("location"), type=reservable_type
            ).order_by("-is_reservable")

        return form

    def form_valid(self, form):
        """Add the user who made the reservation to the Reservation instance."""
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Include the location and available type filters in the context data."""
        context = super().get_context_data(**kwargs)
        location = self.kwargs.get("location")
        context["location"] = location
        context["selected_reservable_type"] = self.request.GET.get("reservable_type")
        context["reservable_types"] = (
            ReservableType.objects.filter(reservable__location=location)
            .distinct()
            .order_by("name")
        )
        return context

    def get_queryset(self):
        """Only show instances of Reservation made by the user."""
        return Reservation.objects.filter(user=self.request.user)

    @staticmethod
    def check_availability(request):
        """Check if an item is available during the given timeslot.

        Excluding the to be updated reservation as conflict.
        """
        start = request.GET.get("start")
        end = request.GET.get("end")
        reservable_id = request.GET.get("reservable")
        object_pk = request.GET.get("object_pk")

        if start < end:
            conflicts = (
                Reservation.objects.exclude(pk=object_pk)
                .filter(reservable_id=reservable_id)
                .filter(
                    Q(start__range=(start, end))
                    | Q(end__range=(start, end))
                    | Q(start__lt=start, end__gt=end)
                )
            )
            available = not conflicts.exists()
        else:
            available = False

        return JsonResponse({"available": available})


class BoatLogbookView(LoginRequiredMixin, FormView):
    """Handle filling in the post-reservation logbook for boats."""

    form_class = BoatLogbookForm
    template_name = "reservations/boat_logbook_form.html"

    def dispatch(self, request, *args, **kwargs):
        """Find the reservation and ensure the logbook can be filled."""
        self.reservation = get_object_or_404(
            Reservation, pk=kwargs["pk"], user=request.user
        )
        if not self.reservation.can_fill_logbook:
            return redirect("reservations:reservation-detail", pk=self.reservation.pk)

        try:
            self.object = self.reservation.boat_logbook
        except BoatLogbook.DoesNotExist:
            self.object = None

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Include the reservation and current damage records in the context."""
        context = super().get_context_data(**kwargs)
        context["reservation"] = self.reservation
        context["damage_records"] = BoatDamageRecord.objects.filter(
            boat_id=self.reservation.reservable_id
        ).order_by("-created")
        return context

    def get_form_kwargs(self):
        """Use an existing logbook instance when editing."""
        kwargs = super().get_form_kwargs()
        if self.object is not None:
            kwargs["instance"] = self.object
        return kwargs

    def form_valid(self, form):
        """Save the logbook and report any newly discovered damage."""
        boat = ReservableBoat.objects.get(pk=self.reservation.reservable_id)
        logbook = form.save(commit=False)
        logbook.reservation = self.reservation
        logbook.save()

        damage_description = form.cleaned_data.get("new_damage_description", "").strip()
        if form.cleaned_data.get("has_new_damage") and damage_description:
            BoatDamageRecord.objects.create(boat=boat, description=damage_description)

        return redirect(self.get_success_url())

    def get_success_url(self):
        """Redirect back to the reservation detail page."""
        return reverse(
            "reservations:reservation-detail", kwargs={"pk": self.reservation.pk}
        )


class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    """Reservation delete view."""

    model = Reservation
    context_object_name = "reservation"
    template_name = "reservations/reservation_confirm_delete.html"
    success_url = reverse_lazy("reservations:reservations")

    def get_context_data(self, **kwargs):
        """Include the request status in the context data."""
        context = super().get_context_data(**kwargs)
        context["RequestStatus"] = Reservation.RequestStatus
        return context


class ReservationDetailView(LoginRequiredMixin, DetailView):
    """Reservation detail view."""

    model = Reservation
    context_object_name = "reservation"

    def get_context_data(self, **kwargs):
        """Include the request status in the context data."""
        context = super().get_context_data(**kwargs)
        context["RequestStatus"] = Reservation.RequestStatus
        return context

    def get_queryset(self):
        """Only show instances of Reservation made by the user."""
        return Reservation.objects.filter(user=self.request.user)
