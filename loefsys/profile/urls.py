"""Module containing the url definition of the sign up page."""

from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    AccountinfoView,
    AccountinfoeditView,
    DeleteAccountView,
    ProfileLoginView,
    ProfilePasswordResetCompleteView,
    ProfilePasswordResetConfirmView,
    ProfilePasswordResetDoneView,
    ProfilePasswordResetView,
    ProfileSignupView,
)

urlpatterns = [
    path("", AccountinfoView.as_view(), name="accountinfo"),
    path("signup/", ProfileSignupView.as_view(), name="signup"),
    path("login/", ProfileLoginView.as_view(), name="login"),
    path("password-reset/", ProfilePasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        ProfilePasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        ProfilePasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        ProfilePasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("edit", AccountinfoeditView.as_view(), name="accountinfoedit"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),
]
