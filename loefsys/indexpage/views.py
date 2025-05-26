"""Module defining the view for the index page."""

from datetime import datetime

from django.shortcuts import render
from django.views.generic import View

from loefsys.events.models import Event


class IndexpageView(View):
    """View for loading the index page."""

    def get(self, request):
        """Handle the get request for the index page."""
        announcements = [
            {
                "header": "Vul je logboek in!",
                "text": "Je hebt je logboek voor Scylla van 11-11 nog niet ingevuld.",
            },
            {
                "header": "Zeilseizoen start weer!",
                "text": "Het zeilseizoen gaat weer van start",
            },
        ]
        events = Event.objects.filter(start__gte=datetime.now()).order_by("start")
        if self.request.user.is_active:
            events = events[:2]
        else:
            events = events.filter(published=True)[:2]
        return render(
            request, "index.html", {"announcements": announcements, "events": events}
        )
