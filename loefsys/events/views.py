"""Module defining the views for events."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, FormView, TemplateView

from loefsys.events.exceptions import NoUserObjectError
from loefsys.events.models.feed_token import FeedToken

from .exceptions import RegistrationError
from .forms import EventFieldsForm
from .models import Event, EventRegistration, RegistrationFormField
from .models.choices import RegistrationStatus


class EventView(DetailView, LoginRequiredMixin):
    """View for viewing an event."""

    model = Event
    template_name = "events/event.html"
    event = None

    def get_context_data(self, **kwargs):
        """Add variables to the context.

        The template needs these variables to render the correct page.
        (E.g. whether to render the registration or cancellation button.)
        """
        if not self.get_object().published:
            raise Http404("Not found")

        context = super().get_context_data(**kwargs)
        context["registration_active"] = (
            self.get_registrations_for_current_user().count() > 0
        )
        context["queue_position"] = (
            0
            if self.get_object()
            .eventregistration_set.queued()
            .filter(contact=self.request.user)
            .count()
            == 0
            else EventRegistration.objects.filter(
                created__lt=EventRegistration.objects.get(
                    contact=self.request.user,
                    event=self.get_object(),
                    status=RegistrationStatus.QUEUED,
                ).created,
                event=self.get_object(),
                status=RegistrationStatus.QUEUED,
            ).count()
            + 1
        )
        context["num_registrations"] = (
            self.get_object().eventregistration_set.active().count()
        )
        context["fine_amount_display"] = f"{self.get_object().fine:.2f}".replace(
            ".", ","
        )
        return context

    def get_object(self, queryset=None):  # noqa ARG002
        """Get event object based on url arguments."""
        if "pk" in self.kwargs:
            return get_object_or_404(Event, pk=self.kwargs["pk"])
        return get_object_or_404(Event, slug=self.kwargs["slug"])

    def post(self, request, *args, **kwargs):  # noqa ARG002
        """Handle the post request for the event view."""
        event = self.get_object()
        action = request.POST.get("action")
        if action == "register":
            # Check registration deadline
            if self.get_object().registrations_open():
                try:
                    register = EventRegistration(
                        event=event,
                        contact=request.user,
                        price_at_registration=event.price,
                        fine_at_registration=event.fine,
                        costs_paid=0.00,
                    )
                    register.save()
                    if event.has_form_fields:
                        return redirect("events:registration", slug=event.slug)
                except IntegrityError:
                    # TODO handle the error
                    print("Registration already exists")
        elif action == "cancel":
            # Only cancel if cancellation deadline is NOT due or
            # it is due and consent was given to be fined
            if (
                not self.get_object().cancelation_deadline < timezone.now()
                or request.POST.get("fine-consent") is not None
            ):
                self.get_registrations_for_current_user().first().cancel()

        return redirect(event)

    def get_registrations_for_current_user(self):
        """Get active registrations for logged in user."""
        return EventRegistration.objects.filter(
            Q(status=RegistrationStatus.ACTIVE) | Q(status=RegistrationStatus.QUEUED),
            event=self.get_object(),
            contact=self.request.user,
        )


class RegistrationFormView(FormView, LoginRequiredMixin):
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


# TODO fix that use of login required is not used double here
class CalendarView(DetailView, LoginRequiredMixin):
    """View for displaying the event calendar."""

    @method_decorator(login_required)
    def get(self, request):
        """Return the calendar view."""
        return render(request, "events/calendar.html")


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
