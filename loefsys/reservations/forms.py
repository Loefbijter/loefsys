"""Module defining the forms for the reservations."""

from django import forms
from django.utils.translation import gettext_lazy as _

from loefsys.members.models.user import User

from .models import Reservable, Reservation


class CreateReservationForm(forms.ModelForm):
    """A form to create reservations."""

    reservable = forms.ModelChoiceField(
        label=_("Te reserveren item"),
        queryset=Reservable.objects.none(),
        widget=forms.RadioSelect,
    )
    authorized_userskippership = forms.ModelChoiceField(
        label=_("Kies een schipper"),
        queryset=User.objects.filter(is_active=True).order_by(
            "last_name", "first_name"
        ),
        required=False,
        empty_label=_("Geen schipper geselecteerd"),
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

    @property
    def reserved_item(self):
        """Return the selected reservable item."""
        return self["reservable"]

    class Meta:
        model = Reservation
        fields = ("reservable", "start", "end", "authorized_userskippership")


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
    sort_by = forms.ChoiceField(choices=CHOICES, required=False)
