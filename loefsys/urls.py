"""Module containing the url definition of the loefsys web app."""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.main, name="main"),
    path("signup/", views.signup, name="signup_page"),
    path("admin/", admin.site.urls),
    path("reservations/", include("loefsys.reservations.urls")),
    *debug_toolbar_urls(),
]
