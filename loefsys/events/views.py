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
from .models import Event, EventRegistration, RegistrationFormField
from .models.choices import RegistrationStatus


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
        }

    def post(self, request, *_args, **_kwargs):
        """Handle the post request for the event view."""
        self.object = self.get_object()
        action = request.POST.get("action")
        if action == "register":
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
                if self.object.has_form_fields:
                    return redirect("events:registration", slug=self.object.slug)
            except IntegrityError:
                print("Registration already exists")

    def cancel_registration(self, request):
        """Cancel the registration for the current user and event."""
        # Only cancel if cancellation deadline is NOT due or
        # it is due and consent was given to be fined
        if (
            self.get_object().cancelation_window_open()
            or request.POST.get("fine-consent") is not None
        ):
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

    def get_registration_button_text(
        self, registration: EventRegistration | None
    ) -> str:
        """Determine the text for the registration button for user and event status."""
        obj = self.object
        text = _("Inschrijven")  # Default text for users without registration
        if registration:
            deadline = obj.cancelation_deadline or obj.registration_deadline
            if registration.get_queue_position is not None:
                text = _("Verlaat wachtrij")
            elif obj.cancelation_window_open():
                text = _("Afmelden")
            elif obj.fine_on_cancellation():
                text = _("Afmelden (met boete)")
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
            return not self.object.cancelation_window_open()

        return not self.object.registrations_open()

    def get_registration_disabled_reason(
        self, registration: EventRegistration | None
    ) -> str:
        """Return the reason why registration is disabled."""
        obj = self.object
        if registration is not None:
            if obj.cancelation_window_open():
                return ""
            if obj.fine_on_cancellation():
                return _("Afmelden kan leiden tot een boete.")
            return _("Afmelden is niet meer mogelijk.")

        if not obj.published:
            return _(
                "Inschrijvingen zijn niet geopend omdat dit evenement niet gepubliceerd is."
            )
        if (
            obj.registration_start is not None
            and timezone.now() < obj.registration_start
        ):
            return _("Inschrijven vanaf %(date)s.") % {
                "date": date_format(obj.registration_start, "DATETIME_FORMAT")
            }
        if (
            obj.registration_deadline is None
            or timezone.now() > obj.registration_deadline
        ):
            if obj.registration_deadline is None:
                return _("Inschrijvingen zijn gesloten.")
            return _("Inschrijvingen zijn gesloten op %(date)s.") % {
                "date": date_format(obj.registration_deadline, "DATETIME_FORMAT")
            }

        return _("Inschrijvingen zijn momenteel gesloten.")


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
        except EventRegistration.DoesNotExist as error:
            raise RegistrationError(
                _("You are not registered for this event.")
            ) from error
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
                    "value": value,
                },
            )
            for field, value in registration.form_fields
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
