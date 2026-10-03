"""Module containing the url definition of the home page."""

from django.urls import path

from .views import (
    AssociationInformationView,
    HomeView,
    SchippersView,
    SchipperschapView,
    StyleguideView,
    VereningingslidView,
)

app_name = "home"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path(
        "association-information/",
        AssociationInformationView.as_view(),
        name="association-information",
    ),
    path("schippers/", SchippersView.as_view(), name="schippers"),
    path("schipperschap/", SchipperschapView.as_view(), name="schipperschap"),
    path("styleguide/", StyleguideView.as_view(), name="styleguide"),
    path("verenigingslied/", VereningingslidView.as_view(), name="verenigingslied"),
]
