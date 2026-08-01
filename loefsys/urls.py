"""Module containing the url definition of the loefsys web app."""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("loefsys.home.urls"), name="home"),
    path("", include("loefsys.members.urls", namespace="members")),
    # path("profile/", include("loefsys.profile.urls"), name="profile"),
    path("reservations/", include("loefsys.reservations.urls"), name="reservations"),
    path("events/", include("loefsys.events.urls"), name="events"),
    path("__reload__/", include("django_browser_reload.urls")),
    *debug_toolbar_urls(),
]

handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
