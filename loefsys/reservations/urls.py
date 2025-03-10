"""Module containing the url definition of the reservations app."""

from django.urls import path

from .views import (
    ReservationCreateView,
    ReservationDeleteView,
    ReservationDetailView,
    ReservationUpdateView,
)

urlpatterns = [
    path("add/", ReservationCreateView.as_view(), name="reservation-add"),
    path("update/<int:pk>", ReservationUpdateView.as_view(), name="reservation-update"),
    path("delete/<int:pk>", ReservationDeleteView.as_view(), name="reservation-delete"),
    path("detail/<int:pk>", ReservationDetailView.as_view(), name="reservation-detail"),
]
