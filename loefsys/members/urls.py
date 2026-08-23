"""Urls of the members app."""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from django.views.generic import TemplateView

from .views import (
    ProfileView,
    UserProfileEditView,
    UserProfileView,
    UserSetPasswordView,
)

# keep LoginView/LogoutView imports above

app_name = "members"

urlpatterns_profiles = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("profile/edit/", UserProfileEditView.as_view(), name="user-profile-edit"),
    path(
        "profile/set-password/", UserSetPasswordView.as_view(), name="user-set-password"
    ),
    path("profile/<slug:slug>/", ProfileView.as_view(), name="profile"),
]

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(template_name="login.html", next_page="/"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    # Password reset disabled — point users to contact the web committee
    path(
        "reset-password/",
        TemplateView.as_view(template_name="registration/reset_disabled.html"),
        name="reset-password",
    ),
    path(
        "reset-password/done/",
        TemplateView.as_view(template_name="registration/reset_disabled.html"),
        name="reset-password-done",
    ),
    path("profiles/", include(urlpatterns_profiles)),
]
