"""Module defining the class-based views for the reservations."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from loefsys.reservations.forms import CreateReservationForm, SortByReservationForm
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

        return (
            Reservation.objects.filter(user=self.request.user, start__gt=timezone.now())
            .exclude(request_status=Reservation.RequestStatus.DENIED)
            .order_by(sort_by)
        )

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
                location=self.kwargs.get("location"), reservable_type=reservable_type
            ).order_by("-is_reservable")

        return form

    def form_valid(self, form):
        """Add the user who made the reservation to the Reservation instance."""
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Include the location in the context data."""
        context = super().get_context_data(**kwargs)
        context["location"] = self.kwargs.get("location")
        context["selected_reservable_type"] = self.request.GET.get("reservable_type")
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
                location=self.kwargs.get("location"), reservable_type=reservable_type
            ).order_by("-is_reservable")

        return form

    def form_valid(self, form):
        """Add the user who made the reservation to the Reservation instance."""
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Include the location in the context data."""
        context = super().get_context_data(**kwargs)
        context["location"] = self.kwargs.get("location")
        context["selected_reservable_type"] = self.request.GET.get("reservable_type")
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


class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    """Reservation delete view."""

    model = Reservation
    template_name = "reservations/reservation_confirm_delete.html"
    success_url = reverse_lazy("reservations:reservations")


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
