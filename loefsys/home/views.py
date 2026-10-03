"""Module defining the view for the index page."""

from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, View

from loefsys.events.models import Event, EventRegistration
from loefsys.events.models.choices import RegistrationStatus
from loefsys.home.models import Announcement
from loefsys.members.models import UserSkippership
from loefsys.reservations.models import ReservableType
from loefsys.reservations.models.reservation import Reservation


class HomeView(View):
    """The member dashboard: next activity, things to do and what is coming up."""

    UPCOMING_LIMIT = 4

    @staticmethod
    def greeting(now) -> str:
        """Return a greeting that fits the local time of day."""
        hour = timezone.localtime(now).hour
        if hour < 6:  # noqa: PLR2004
            return _("Good night")
        if hour < 12:  # noqa: PLR2004
            return _("Good morning")
        if hour < 18:  # noqa: PLR2004
            return _("Good afternoon")
        return _("Good evening")

    def get(self, request):
        """Handle the get request for the index page."""
        now = timezone.now()
        user = request.user
        announcements = Announcement.objects.filter(
            published=True, announcement_start__lte=now, announcement_end__gte=now
        ).order_by("-announcement_start")
        events = Event.objects.filter(start__gte=now).order_by("start")
        if not user.is_active:
            events = events.filter(published=True)

        next_registration = None
        user_reservations = None
        logbook_todo: list[Reservation] = []
        skipperships: list = []
        pending_approvals: list[Reservation] | None = None
        if user.is_authenticated:
            next_registration = (
                EventRegistration.objects.filter(
                    contact=user,
                    event__end__gte=now,
                    status__in=(RegistrationStatus.ACTIVE, RegistrationStatus.QUEUED),
                )
                .select_related("event")
                .order_by("event__start")
                .first()
            )
            user_reservations = (
                Reservation.objects.filter(user=user, end__gt=now)
                .exclude(request_status=Reservation.RequestStatus.DENIED)
                .select_related("reservable__type")
                .order_by("start")[: self.UPCOMING_LIMIT]
            )
            logbook_todo = list(
                Reservation.objects.filter(
                    user=user,
                    end__lt=now,
                    reservable__type__category=ReservableType.Category.BOAT,
                    boat_logbook__isnull=True,
                )
                .exclude(request_status=Reservation.RequestStatus.DENIED)
                .select_related("reservable")
                .order_by("-start")
            )
            skipperships = highest_skipperships(user)
            if user.is_staff:
                pending_approvals = list(
                    Reservation.objects.filter(
                        request_status=Reservation.RequestStatus.PENDING
                    )
                    .select_related("reservable", "user")
                    .order_by("start")[: self.UPCOMING_LIMIT]
                )

        next_event = next_registration.event if next_registration else None
        upcoming_events = list(
            events.exclude(pk=next_event.pk) if next_event else events
        )[: self.UPCOMING_LIMIT]

        context = {
            "greeting": self.greeting(now),
            "announcements": announcements,
            "events": events,
            "upcoming_events": upcoming_events,
            "next_event": next_event,
            "next_registration": next_registration,
            "user_reservations": user_reservations,
            "logbook_todo": logbook_todo,
            "skipperships": skipperships,
            "pending_approvals": pending_approvals,
            "todo_count": len(logbook_todo)
            + (len(pending_approvals) if pending_approvals is not None else 0),
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


def highest_skipperships(user) -> list:
    """Return the user's skipperships, leaving out the ones implied by a higher one."""
    entries = list(user.user_skipperships.select_related("skippership__parent"))
    return [
        entry.skippership
        for entry in entries
        if not any(
            _is_ancestor_of(other.skippership, entry.skippership)
            for other in entries
            if other.skippership_id != entry.skippership_id
        )
    ]


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
        user_skipperships_by_user: dict[int, list] = {}
        for user_skippership in user_skipperships:
            user_skipperships_by_user.setdefault(user_skippership.user_id, []).append(
                user_skippership
            )

        grouped_skippers: dict[str, list] = {}
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
        context["skipper_count"] = len(user_skipperships_by_user)
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
