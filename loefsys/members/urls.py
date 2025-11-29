"""Urls of the members app."""

from django.contrib.auth.views import LoginView
from django.urls import include, path

from .views import ProfileView, UserProfileEditView, UserProfileView

app_name = "members"

urlpatterns_profiles = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("profile/edit/", UserProfileEditView.as_view(), name="user-profile-edit"),
    path("profile/<slug:slug>/", ProfileView.as_view(), name="profile"),
]

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(template_name="login.html", next_page="/"),
        name="login",
    ),
    path("reset-password/", ProfileView.as_view(), name="reset-password"),
    path("profiles/", include(urlpatterns_profiles)),
]
