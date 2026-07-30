"""Module defining the view for the index page."""

from datetime import datetime

from django.shortcuts import render
from django.views.generic import TemplateView, View

from loefsys.events.models import Event
from loefsys.home.models import Announcement


class HomeView(View):
    """View for loading the index page."""

    def get(self, request):
        """Handle the get request for the index page."""
        announcements = Announcement.objects.filter(
            published=True,
            announcement_start__lte=datetime.now(),
            announcement_end__gte=datetime.now(),
        ).order_by("-announcement_start")
        events = Event.objects.filter(start__gte=datetime.now()).order_by("start")
        if not self.request.user.is_active:
            events = events.filter(published=True)
        context = {"announcements": announcements, "events": events}
        return render(request, "home/index.html", context)


class AssociationInformationView(TemplateView):
    """View for displaying association information page."""

    template_name = "home/association-information.html"


class SchipperschapView(TemplateView):
    """View for displaying schipperschap page."""

    template_name = "home/schipperschap.html"


class StyleguideView(TemplateView):
    """View for displaying styleguide page."""

    template_name = "home/styleguide.html"


class VereningingslidView(TemplateView):
    """View for displaying verenigingslied page."""

    template_name = "home/verenigingslied.html"
