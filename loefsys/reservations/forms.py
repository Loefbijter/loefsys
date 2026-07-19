"""Module defining the forms for the reservations."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Reservable, Reservation


class CreateReservationForm(forms.ModelForm):
    """A form to create reservations."""

    reservable = forms.ModelChoiceField(
        label=_("Te reserveren item"),
        queryset=Reservable.objects.none(),
        widget=forms.RadioSelect,
    )
    start = forms.DateTimeField(
        label=_("Starttijd"),
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
    )
    end = forms.DateTimeField(
        label=_("Eindtijd"),
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
    )

    class Meta:
        model = Reservation
        fields = ("reservable", "start", "end")


class SortByReservationForm(forms.Form):
    """A form to sort reservations."""

    CHOICES = (
        ("start", _("Starttijd")),
        ("end", _("Eindtijd")),
        ("location", _("Locatie")),
        ("-created", _("Nieuwste eerst")),
        ("A-Z", _("A-Z")),
        ("type", _("Type")),
    )
    sort_by = forms.ChoiceField(label=_("Sorteer op"), choices=CHOICES, required=False)
