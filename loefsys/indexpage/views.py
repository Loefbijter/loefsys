"""Module defining the view for the index page."""

from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import View

from loefsys.events.models import Event
from loefsys.indexpage.models import Announcement


class IndexpageView(LoginRequiredMixin, View):
    """View for loading the index page."""

    def get(self, request):
        """Handle the get request for the index page."""
        announcements = Announcement.objects.filter(
            published=True,
            announcement_start__lte=datetime.now(),
            announcement_end__gte=datetime.now(),
        ).order_by("-announcement_start")
        announcements = announcements[:2]
        events = Event.objects.filter(start__gte=datetime.now()).order_by("start")
        if self.request.user.is_active:
            events = events[:2]
        else:
            events = events.filter(published=True)[:2]
        return render(
            request, "main.html", {"announcements": announcements, "events": events}
        )
