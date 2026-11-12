"""Module containing the url definition of the loefsys web app."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
)
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic import RedirectView
from django.views.i18n import set_language
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    # There is no CommonMiddleware, so APPEND_SLASH does not redirect /admin.
    path("admin", RedirectView.as_view(url="/admin/", permanent=True)),
    # Public, so visitors can pick a language before logging in.
    path("i18n/setlang/", login_not_required(set_language), name="set_language"),
    # Provide a top-level named login URL to support templates using {% url 'login' %}.
    path(
        "login/",
        LoginView.as_view(template_name="login.html", next_page="/"),
        name="login",
    ),
    # Top-level password reset confirm/complete views.
    # Support token-based links without the app namespace.
    # The re_path accepts empty uid/token to avoid Reverse errors in some templates.
    re_path(
        r"^reset/(?P<uidb64>[^/]*)/(?P<token>[^/]*)/$",
        PasswordResetConfirmView.as_view(
            template_name="registration/reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="registration/reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("", include("loefsys.home.urls"), name="home"),
    path("", include("loefsys.members.urls", namespace="members")),
    # path("profile/", include("loefsys.profile.urls"), name="profile"),
    path("reservations/", include("loefsys.reservations.urls"), name="reservations"),
    path("events/", include("loefsys.events.urls"), name="events"),
]

if settings.DEBUG and settings.BROWSER_RELOAD_ENABLED:
    from django_browser_reload.views import events

    urlpatterns.append(
        path(
            "__reload__/",
            include(
                (
                    [path("events/", login_not_required(events), name="events")],
                    "django_browser_reload",
                )
            ),
        )
    )

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()

handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        view=login_not_required(serve),
        document_root=settings.MEDIA_ROOT,
    )
