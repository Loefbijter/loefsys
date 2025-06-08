"""Module containing the url definition of the loefsys web app."""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("loefsys.indexpage.urls")),
    path("admin/", admin.site.urls),
    path("profile/", include("loefsys.profile.urls")),
    # path("account/", include("loefsys.accountinfopage.urls")),
    path("reservations/", include("loefsys.reservations.urls")),
    path("events/", include("loefsys.events.urls")),
    *debug_toolbar_urls(),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
