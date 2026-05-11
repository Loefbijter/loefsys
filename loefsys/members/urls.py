"""Urls of the members app."""

from django.contrib.auth import views as auth_views
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
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/"),
        name="logout",
    ),
    path(
        "reset-password/", 
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html",
            email_template_name="password_reset_email.html",
            success_url="/reset-password/done/"
        ), 
        name="reset-password"
    ),
    path(
        "reset-password/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
        name="password_reset_done"
    ),
    path(
        "reset-password/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html",
            success_url="/reset-password/complete/"
        ),
        name="password_reset_confirm"
    ),
    path(
        "reset-password/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
        name="password_reset_complete"
    ),
    path("profiles/", include(urlpatterns_profiles)),
]
