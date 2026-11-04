"""Urls of the members app."""

from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.urls import include, path, reverse_lazy
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
    # Members request a link by email; the link opens the top-level
    # ``password_reset_confirm`` view, where they choose a new password.
    path(
        "reset-password/",
        PasswordResetView.as_view(
            template_name="registration/reset_form.html",
            email_template_name="registration/loefsys_password_reset_email.txt",
            subject_template_name="registration/loefsys_password_reset_subject.txt",
            success_url=reverse_lazy("members:reset-password-done"),
        ),
        name="reset-password",
    ),
    path(
        "reset-password/done/",
        TemplateView.as_view(template_name="registration/reset_done.html"),
        name="reset-password-done",
    ),
    path("profiles/", include(urlpatterns_profiles)),
]
