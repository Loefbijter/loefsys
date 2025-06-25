"""Module containing the url definition of the reservations app."""

from django.urls import path

from .views import (
    LogCreateView,
    ReservationCreateView,
    ReservationDeleteView,
    ReservationDetailView,
    ReservationListView,
    ReservationUpdateView,
)

app_name = "reservations"

urlpatterns = [
    path("", ReservationListView.as_view(), name="reservations"),
    path("add/<int:location>", ReservationCreateView.as_view(), name="reservation-add"),
    path(
        "update/<int:pk>/<int:location>",
        ReservationUpdateView.as_view(),
        name="reservation-update",
    ),
    path("delete/<int:pk>", ReservationDeleteView.as_view(), name="reservation-delete"),
    path("detail/<int:pk>", ReservationDetailView.as_view(), name="reservation-detail"),
    path(
        "check-availability",
        ReservationCreateView.check_availability,
        name="check-availability",
    ),
    path(
        "update/check-availability",
        ReservationUpdateView.check_availability,
        name="check-availability",
    ),
    path("add/log/<int:pk>", LogCreateView.as_view(), name="log-add"),
]
