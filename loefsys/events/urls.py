"""URL configuration for the events app."""

from django.urls import path

from .feeds import OtherEventFeed, RegisteredEventFeed
from .views import (
    CalendarView,
    EventDetailView,
    EventFeedView,
    EventFillerView,
    MyEventOrganizerDetailView,
    MyEventsView,
    RegistrationFormView,
)

app_name = "events"

urlpatterns = [
    path("organized/", MyEventsView.as_view(), name="my_events"),
    path(
        "organized/<slug:slug>/",
        MyEventOrganizerDetailView.as_view(),
        name="my_events_event",
    ),
    path(
        "<slug:slug>/registration/", RegistrationFormView.as_view(), name="registration"
    ),
    path("<slug:slug>/", EventDetailView.as_view(), name="event"),
    path("", CalendarView.as_view(), name="events"),
    path("event_filler", EventFillerView.as_view(), name="event_filler"),
    path("registeredical", RegisteredEventFeed(), name="registered_event_feed"),
    path("otherical", OtherEventFeed(), name="other_event_feed"),
    path("feed", EventFeedView.as_view(), name="event_feed_view"),
]
