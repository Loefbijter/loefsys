"""Module defining the forms for the reservations."""

from typing import ClassVar

from django import forms
from django.utils.translation import gettext_lazy as _

from loefsys.members.models.user import User

from .models import BoatLogbook, Reservable, Reservation


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


class BoatLogbookForm(forms.ModelForm):
    """A form to fill in a boat logbook after a reservation."""

    has_new_damage = forms.BooleanField(
        label=_("Heb je nieuwe schade ontdekt?"), required=False
    )
    new_damage_description = forms.CharField(
        label=_("Beschrijf de nieuwe schade"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    class Meta:
        model = BoatLogbook
        fields = (
            "wind_force",
            "motor_hours",
            "refueled",
            "has_new_damage",
            "new_damage_description",
            "photo",
        )
        # Labels may be lazy translation strings; use a wide type to satisfy
        # static checkers while remaining compatible with Django forms.
        labels: ClassVar[dict[str, object]] = {
            "wind_force": _("Wat was de windkracht? (Bft)"),
            "motor_hours": _("Hoeveel motoruren heb je gemaakt?"),
            "refueled": _("Heb je de boot afgetankt?"),
            "photo": _("Voeg een foto van de boot toe"),
        }

    def clean(self):
        """Require a damage description when the user reports new damage."""
        cleaned_data = super().clean()
        # Be defensive: the description can be None, so coerce to empty string
        # before calling string operations.
        if cleaned_data.get("has_new_damage"):
            desc = cleaned_data.get("new_damage_description") or ""
            if not desc.strip():
                self.add_error(
                    "new_damage_description",
                    _(
                        "Beschrijf de nieuwe schade als je aangeeft dat er nieuwe "
                        "schade is."
                    ),
                )
        return cleaned_data
