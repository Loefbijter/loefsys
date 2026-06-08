"""Module defining the forms for the reservations."""

from django import forms

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
        ("start", "Starttijd"),
        ("end", "Eindtijd"),
        ("location", "Locatie"),
        ("-date_of_creation", "Nieuwste eerst"),
        ("A-Z", "A-Z"),
        ("type", "Type"),
    )
    sort_by = forms.ChoiceField(choices=CHOICES, required=False)
