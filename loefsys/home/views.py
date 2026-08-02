"""Module defining the view for the index page."""

from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View

# Length used when building a short preview of long descriptions
DESCRIPTION_PREVIEW_LEN = 300

from loefsys.events.models import Event
from loefsys.home.models import Announcement
from loefsys.members.models import UserSkippership
from loefsys.reservations.models.reservation import Reservation


class HomeView(View):
    """View for loading the index page."""

    def get(self, request):
        """Handle the get request for the index page."""
        now = timezone.now()
        announcements = Announcement.objects.filter(
            published=True, announcement_start__lte=now, announcement_end__gte=now
        ).order_by("-announcement_start")
        events = Event.objects.filter(start__gte=now).order_by("start")
        if not self.request.user.is_active:
            events = events.filter(published=True)

        # Show top 4 upcoming events as a preview
        raw_upcoming = list(events[:4])
        upcoming_events = []
        for ev in raw_upcoming:
            # Picture URL if available
            ev.picture_url = (
                ev.picture.url
                if getattr(ev, "picture", None) and getattr(ev.picture, "url", None)
                else None
            )

            # Seats taken and spots left if capacity is defined
            try:
                ev.seats_taken = ev.eventregistration_set.active().count()
            except Exception:
                # Fallback: count all registrations if custom manager not available
                ev.seats_taken = ev.eventregistration_set.count()
            ev.spots_left = (ev.capacity - ev.seats_taken) if ev.capacity else None

            # Flags computed via model methods
            try:
                ev.registrations_open_flag = ev.registrations_open()
            except Exception:
                ev.registrations_open_flag = False
            try:
                ev.max_capacity_reached_flag = ev.max_capacity_reached()
            except Exception:
                ev.max_capacity_reached_flag = False

            # Human readable category and truncated description
            ev.category_display = (
                ev.get_category_display() if hasattr(ev, "get_category_display") else ""
            )
            if ev.description:
                ev.description_preview = ev.description[:DESCRIPTION_PREVIEW_LEN] + (
                    "..." if len(ev.description) > DESCRIPTION_PREVIEW_LEN else ""
                )
            else:
                ev.description_preview = ""

            upcoming_events.append(ev)

        # User-specific reservations (upcoming)
        user_reservations = None
        if request.user.is_authenticated:
            user_reservations = (
                Reservation.objects.filter(user=request.user, end__gt=now)
                .exclude(request_status=Reservation.RequestStatus.DENIED)
                .order_by("start")[:4]
            )

        # Pending approvals for staff
        pending_approvals = None
        if request.user.is_staff:
            pending_approvals = Reservation.objects.filter(
                request_status=Reservation.RequestStatus.PENDING
            ).order_by("start")[:4]

        context = {
            "announcements": announcements,
            "events": events,
            "upcoming_events": upcoming_events,
            "user_reservations": user_reservations,
            "pending_approvals": pending_approvals,
            "RequestStatus": Reservation.RequestStatus,
        }
        return render(request, "home/index.html", context)


class AssociationInformationView(TemplateView):
    """View for displaying association information page."""

    template_name = "home/association-information.html"


def _is_ancestor_of(skippership, ancestor):
    """Return whether ``ancestor`` is part of the parent chain for ``skippership``."""
    current = skippership
    while current is not None:
        if current.pk == ancestor.pk:
            return True
        current = current.parent
    return False


class SchippersView(TemplateView):
    """View for displaying all skippers grouped by their furthest skippership."""

    template_name = "home/schippers.html"

    def get_context_data(self, **kwargs):
        """Add a grouped list of skippers to the page context."""
        context = super().get_context_data(**kwargs)

        user_skipperships = list(
            UserSkippership.objects.select_related("user", "skippership").order_by(
                "user__first_name", "user__last_name", "skippership__name"
            )
        )
        user_skipperships_by_user = {}
        for user_skippership in user_skipperships:
            user_skipperships_by_user.setdefault(user_skippership.user_id, []).append(
                user_skippership
            )

        grouped_skippers = {}
        for entries in user_skipperships_by_user.values():
            user = entries[0].user
            for entry in entries:
                if any(
                    _is_ancestor_of(other.skippership, entry.skippership)
                    for other in entries
                    if other.skippership_id != entry.skippership_id
                ):
                    continue

                grouped_skippers.setdefault(entry.skippership.name, []).append(
                    {
                        "user": user,
                        "skippership": entry.skippership,
                        "profile_url": reverse(
                            "members:profile", kwargs={"slug": user.slug}
                        ),
                    }
                )

        skippers_by_group = []
        for group_name in sorted(grouped_skippers):
            group_entries = sorted(
                grouped_skippers[group_name],
                key=lambda entry: entry["user"].display_name.lower(),
            )
            skippers_by_group.append({"label": group_name, "schippers": group_entries})

        context["skippers_by_level"] = skippers_by_group
        context["skipper_groups"] = skippers_by_group
        return context


class SchipperschapView(TemplateView):
    """View for displaying schipperschap page."""

    template_name = "home/schipperschap.html"


class StyleguideView(TemplateView):
    """View for displaying styleguide page."""

    template_name = "home/styleguide.html"


class VereningingslidView(TemplateView):
    """View for displaying verenigingslied page."""

    template_name = "home/verenigingslied.html"
