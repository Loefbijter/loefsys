"""iCalendar feed generation for Loefbijter events."""

from django.db.models import Q
from django_ical.views import ICalFeed

from loefsys.events.models import Event
from loefsys.events.models.feed_token import FeedToken


class RegisteredEventFeed(ICalFeed):
    """Generates an iCalendar feed for events the user is registered for."""

    product_id = "-//Loefsys//RegisteredEventCalendar//"
    timezone = "Europe/Amsterdam"
    title = "Registered Loefbijter Events"

    def __call__(self, request, *args, **kwargs):  # noqa: D102
        if "u" in request.GET:
            self.user = FeedToken.get_user(request.GET["u"])
        else:
            self.user = None

        return super().__call__(request, args, kwargs)

    def file_name(self):  # noqa: D102
        return "LoefbijterRegistered.ics"

    def items(self):  # noqa: D102
        query = Q(published=True)

        if self.user:
            query &= Q(eventregistration__contact=self.user)

        return Event.objects.filter(query).order_by("-start")

    def item_title(self, item):  # noqa: D102
        return item.title

    def item_description(self, item):  # noqa: D102
        return item.description

    def item_start_datetime(self, item):  # noqa: D102
        return item.start

    def item_end_datetime(self, item):  # noqa: D102
        return item.end

    def item_location(self, item):  # noqa: D102
        return item.location

    def item_link(self, item):  # noqa: D102
        return item.get_absolute_url()


class OtherEventFeed(ICalFeed):
    """Generates an iCalendar feed for events the user is not registered for."""

    product_id = "-//Loefsys//OtherEventCalendar//"
    timezone = "Europe/Amsterdam"
    title = "Other Loefbijter Events"

    def __call__(self, request, *args, **kwargs):  # noqa: D102
        if "u" in request.GET:
            self.user = FeedToken.get_user(request.GET["u"])
        else:
            self.user = None

        return super().__call__(request, args, kwargs)

    def file_name(self):  # noqa: D102
        return "LoefbijterOther.ics"

    def items(self):  # noqa: D102
        query = Q(published=True)

        if self.user:
            query &= ~Q(eventregistration__contact=self.user)

        return Event.objects.filter(query).order_by("-start")

    def item_title(self, item):  # noqa: D102
        return item.title

    def item_description(self, item):  # noqa: D102
        return item.description

    def item_start_datetime(self, item):  # noqa: D102
        return item.start

    def item_end_datetime(self, item):  # noqa: D102
        return item.end

    def item_location(self, item):  # noqa: D102
        return item.location

    def item_link(self, item):  # noqa: D102
        return item.get_absolute_url()
