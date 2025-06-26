"""Module containing the url definition of the loefsys web app."""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin", admin.site.urls),

    path("", include("loefsys.home.urls"), name="home"),
    path("", include("loefsys.members.urls"), name="members"),

    # path("profile/", include("loefsys.profile.urls"), name="profile"),
    # path("account/", include("loefsys.accountinfopage.urls")),
    path("reservations/", include("loefsys.reservations.urls"), name="reservations"),
    path("events/", include("loefsys.events.urls"), name="events"),

    path("", include("django_components.urls")),
    path("__reload__", include("django_browser_reload.urls")),
    *debug_toolbar_urls(),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
