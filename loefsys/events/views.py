"""Module defining the views for events."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, FormView, TemplateView

from loefsys.events.exceptions import NoUserObjectError
from loefsys.events.models.feed_token import FeedToken

from .exceptions import RegistrationError
from .forms import EventFieldsForm
from .models import Event, EventOrganizer, EventRegistration, RegistrationFormField
from .models.choices import EventCategories, RegistrationStatus


class EventDetailView(LoginRequiredMixin, DetailView):
    """View for viewing an event."""

    model = Event
    queryset = Event.objects.filter(published=True)
    template_name = "events/event.html"

    def get_context_data(self, **kwargs):
        """Add variables to the context.

        Returns
        -------
        The context data for the template as a dictionary wrapping:

        context.registration_active : bool
            Whether the user has an active registration for this event.
        context.queue_position : int | None
            The position in the queue of the user, if applicable.
        context.num_registrations : int
            The number of active registrations for this event.
        context.registration_disabled : bool
            Whether the registration button should be disabled.
        context.can_view_attendees : bool
            Whether the current user is allowed to see the attendee list.
        context.attendees : QuerySet[EventRegistration] | None
            The active registrations for this event, if the user has permission.
        """
        user_registration = self.get_registration_for_current_user()
        can_view_attendees = self.request.user.has_perm("events.view_eventregistration")

        try:
            organizer = self.object.eventorganizer
        except EventOrganizer.DoesNotExist:
            organizer = None

        return super().get_context_data(**kwargs) | {
            "registration_active": user_registration is not None,
            "queue_position": user_registration.get_queue_position
            if user_registration
            else None,
            "num_registrations": self.object.eventregistration_set.active().count(),
            "registration_button_text": self.get_registration_button_text(
                user_registration
            ),
            "registration_disabled": self.get_registration_disabled(user_registration),
            "registration_disabled_reason": self.get_registration_disabled_reason(
                user_registration
            ),
            "can_view_attendees": can_view_attendees,
            "attendees": (
                self.object.eventregistration_set.active().select_related("contact")
                if can_view_attendees
                else None
            ),
            "registration_form": self.get_registration_form(user_registration),
            "show_registration_modal": self.request.GET.get("show_registration_modal")
            == "1",
            "organizer": organizer,
        }

    def post(self, request, *_args, **_kwargs):
        """Handle the post request for the event view."""
        self.object = self.get_object()
        action = request.POST.get("action")
        if action == "register":
            if self.object.has_form_fields:
                return redirect(
                    f"{self.object.get_absolute_url()}?show_registration_modal=1"
                )
            self.create_registration(request.user)
        elif action == "cancel":
            self.cancel_registration(request)

        return redirect(self.object)

    def create_registration(self, user):
        """Create a registration for the current user and event."""
        if self.object.registrations_open():
            try:
                register = EventRegistration(
                    event=self.object,
                    contact=user,
                    price_at_registration=self.object.price,
                    fine_at_registration=self.object.fine,
                    costs_paid=0.00,
                )
                register.save()
            except IntegrityError:
                print("Registration already exists")

    def cancel_registration(self, request):
        """Cancel the registration for the current user and event."""
        event = self.get_object()
        if not event.can_cancel_registration():
            return

        if (
            event.cancellation_fine_required()
            and request.POST.get("fine-consent") is None
        ):
            return

        self.get_registration_for_current_user().cancel()

    def get_registration_for_current_user(self):
        """Get active registrations for logged in user."""
        return (
            self.object.eventregistration_set.for_user(self.request.user)
            .filter(
                Q(status=RegistrationStatus.ACTIVE)
                | Q(status=RegistrationStatus.QUEUED)
            )
            .last()
        )

    def get_registration_form(self, registration=None):
        """Create the form for additional event registration fields."""
        if not self.object.has_form_fields:
            return None

        return EventFieldsForm(
            form_fields=[
                (
                    field.pk,
                    {
                        "subject": field.subject,
                        "type": field.type,
                        "description": field.description,
                        "required": field.required,
                        "default": field.default,
                        "value": field.get_value_for(registration)
                        if registration is not None
                        else None,
                    },
                )
                for field in self.object.registrationformfield_set.all()
            ]
        )

    def get_registration_button_text(
        self, registration: EventRegistration | None
    ) -> str:
        """Determine the text for the registration button for user and event status."""
        obj = self.object
        text = _("Inschrijven")  # Default text for users without registration
        if registration:
            if registration.get_queue_position is not None:
                text = _("Verlaat wachtrij")
            elif not obj.can_cancel_registration():
                text = _("Kan niet afmelden")
            elif obj.cancellation_fine_required():
                text = _("Afmelden (met boete)")
            elif obj.cancelation_window_open():
                text = _("Afmelden")
            else:
                text = _("Kan niet afmelden")
        elif not obj.registrations_open():
            if obj.registration_start and timezone.now() < obj.registration_start:
                text = _("Inschrijven vanaf %(date)s") % {
                    "date": date_format(obj.registration_start, "DATETIME_FORMAT")
                }
            else:
                text = _("Inschrijvingen gesloten")
        elif obj.max_capacity_reached():
            text = _("In wachtrij")
        else:
            text = _("Inschrijven")

        return text

    def get_registration_disabled(self, registration: EventRegistration | None) -> bool:
        """Determine whether the registration button should be disabled."""
        if registration is not None:
            return not self.object.can_cancel_registration()

        return not self.object.registrations_open()

    def get_registration_disabled_reason(
        self, registration: EventRegistration | None
    ) -> str:
        """Return the reason why registration is disabled."""
        obj = self.object
        reason = ""

        if registration is not None:
            if not obj.can_cancel_registration():
                reason = _("Afmelden is niet meer mogelijk.")
            elif obj.cancellation_fine_required():
                reason = _("Afmelden kan leiden tot een boete.")
            else:
                reason = ""
        elif not obj.published:
            reason = _(
                "Inschrijvingen zijn niet geopend omdat dit evenement "
                "niet gepubliceerd is."
            )
        elif obj.registrations_open():
            reason = ""
        elif (
            obj.registration_start is not None
            and timezone.now() < obj.registration_start
        ):
            reason = _("Inschrijven vanaf %(date)s.") % {
                "date": date_format(obj.registration_start, "DATETIME_FORMAT")
            }
        elif obj.registration_deadline is None:
            reason = _("Inschrijvingen zijn gesloten.")
        elif timezone.now() > obj.registration_deadline:
            reason = _("Inschrijvingen zijn gesloten op %(date)s.") % {
                "date": date_format(obj.registration_deadline, "DATETIME_FORMAT")
            }
        else:
            reason = _("Inschrijvingen zijn momenteel gesloten.")

        return reason


class RegistrationFormView(LoginRequiredMixin, FormView):
    """View for the registration form."""

    template_name = "events/registration_form.html"
    form_class = EventFieldsForm
    event = None
    success_url = None

    def __get_registration(self, event, contact):
        """Get the registration for the event and contact.

        Used for updating the registration when additional form fields are filled out.
        This function only retrieves active or queued registrations.
        """
        try:
            registration = EventRegistration.objects.get(
                Q(status=RegistrationStatus.ACTIVE)
                | Q(status=RegistrationStatus.QUEUED),
                event=event,
                contact=contact,
            )
        except EventRegistration.DoesNotExist:
            registration = EventRegistration(
                event=event,
                contact=contact,
                price_at_registration=event.price,
                fine_at_registration=event.fine,
                costs_paid=0.00,
            )
            registration.save()
            return registration
        except EventRegistration.MultipleObjectsReturned as error:
            raise RegistrationError(
                _("Unable to find the right registration.")
            ) from error

        return registration

    def get_form_kwargs(self):
        """Get form keyword arguments."""
        kwargs = super().get_form_kwargs()
        contact = self.request.user
        registration = self.__get_registration(self.event, contact)

        kwargs["form_fields"] = [
            (
                field.pk,
                {
                    "subject": field.subject,
                    "type": field.type,
                    "description": field.description,
                    "required": field.required,
                    "default": field.default,
                    "value": field.get_value_for(registration),
                },
            )
            for field in self.event.registrationformfield_set.all()
        ]

        return kwargs

    def form_valid(self, form):
        """Handle valid form."""
        values = form.field_values()
        registration = self.__get_registration(self.event, self.request.user)

        for field_id, field_value in values:
            field = RegistrationFormField.objects.get(id=field_id)
            field.set_value_for(registration, field_value)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add the event and registration form to the template context."""
        context = super().get_context_data(**kwargs)
        context["event"] = self.event
        return context

    def dispatch(self, request, *args, **kwargs):
        """Return the proper response to a request."""
        self.event = get_object_or_404(Event, slug=self.kwargs["slug"])
        self.success_url = self.event.get_absolute_url()
        if self.event.has_form_fields:
            return super().dispatch(request, *args, **kwargs)

        return redirect(self.success_url)


class CalendarView(LoginRequiredMixin, TemplateView):
    """View for displaying the event calendar."""

    template_name = "events/calendar.html"


class EventFillerView(View):
    """View for the event filler."""

    def get(self, request):  # noqa: ARG002
        """Get the events for the calendar."""
        events = Event.objects.all()
        data = []
        for event in events:
            if event.published:
                data.append(
                    {
                        "title": event.title,
                        "start": event.start,
                        "end": event.end,
                        "url": event.get_absolute_url(),
                        "picture_url": (
                            event.picture.url
                            if getattr(event, "picture", None)
                            and getattr(event.picture, "url", None)
                            else None
                        ),
                    }
                )
        return JsonResponse(data, safe=False)


class EventFeedView(TemplateView, LoginRequiredMixin):
    """View for the event feed."""

    template_name = "events/event_feed.html"

    def get_context_data(self, **kwargs):
        """Get the event feed."""
        context = super().get_context_data(**kwargs)
        if not self.request.user:
            raise NoUserObjectError(
                "There is no user logged in. If you are a superuser, please make an "
                "account first."
            )
        token = FeedToken.objects.get_or_create(user=self.request.user)[0].token
        context["registered_event_feed"] = (
            f"{reverse('events:registered_event_feed')}?u={token}"
        )
        context["other_event_feed"] = f"{reverse('events:other_event_feed')}?u={token}"

        return context


class MyEventsView(LoginRequiredMixin, TemplateView):
    """View for listing the current user's organized events."""

    template_name = "events/my_events.html"

    def get_context_data(self, **kwargs):
        """Return context containing events organized by the current user."""
        context = super().get_context_data(**kwargs)
        context["events"] = (
            Event.objects.filter(eventorganizer__user=self.request.user)
            .distinct()
            .order_by("start")
        )
        return context


class MyEventOrganizerDetailView(LoginRequiredMixin, DetailView):
    """View for organizers to inspect their own event registrations."""

    model = Event
    template_name = "events/my_event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        """Return events organized by the current user for this view."""
        return Event.objects.filter(eventorganizer__user=self.request.user)

    def get_context_data(self, **kwargs):
        """Return context with event details and attendees."""
        context = super().get_context_data(**kwargs)
        context["event_page_url"] = self.object.get_absolute_url()
        context["attendees"] = (
            self.object.eventregistration_set.active().select_related("contact")
        )
        context["event_categories"] = EventCategories
        context["training_event"] = self.object.category == EventCategories.TRAINING
        return context
