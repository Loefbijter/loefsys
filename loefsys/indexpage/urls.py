"""Module containing the url definition of the index page."""

from django.urls import path

from .views import IndexpageView

urlpatterns = [path("", IndexpageView.as_view(), name="index")]
