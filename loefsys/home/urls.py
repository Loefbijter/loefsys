"""Module containing the url definition of the home page."""

from django.urls import path

from .views import HomeView

urlpatterns = [path("", HomeView.as_view(), name="home")]
