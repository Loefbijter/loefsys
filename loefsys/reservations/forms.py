"""Module defining the forms for the reservations."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Reservable, Reservation


class CreateReservationForm(forms.ModelForm):
    """A form to create reservations."""

    reserved_item = forms.ModelChoiceField(
        queryset=Reservable.objects.none(), widget=forms.RadioSelect
    )
    start = forms.DateTimeField(
        input_formats=["%I:%M %p %d-%b-%Y"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%I:%M %p %d-%b-%Y"
        ),
    )
    end = forms.DateTimeField(
        input_formats=["%I:%M %p %d-%b-%Y"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%I:%M %p %d-%b-%Y"
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
