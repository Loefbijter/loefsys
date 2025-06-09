"""URL configuration for the events app."""

from django.urls import path

from .feeds import OtherEventFeed, RegisteredEventFeed
from .views import (
    CalendarView,
    EventFeedView,
    EventFillerView,
    EventView,
    RegistrationFormView,
)

app_name = "events"

urlpatterns = [
    path("<int:pk>/", EventView.as_view(), name="event"),
    path("<slug:slug>/", EventView.as_view(), name="event"),
    path(
        "<slug:slug>/registration/", RegistrationFormView.as_view(), name="registration"
    ),
    path("", CalendarView.as_view(), name="events"),
    path("event_filler", EventFillerView.as_view(), name="event_filler"),
    path("registeredical", RegisteredEventFeed(), name="registered_event_feed"),
    path("otherical", OtherEventFeed(), name="other_event_feed"),
    path("feed", EventFeedView.as_view(), name="event_feed_view"),
]
