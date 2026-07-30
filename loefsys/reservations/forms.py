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
    sort_by = forms.ChoiceField(choices=CHOICES, required=False)


class CreateLogForm(forms.ModelForm):
    """Form for all fields associated with an event."""

    def __init__(self, *args, **kwargs):
        self.form_fields = kwargs.pop("form_fields")
        super().__init__(*args, **kwargs)

        for k, field in self.form_fields:
            key = str(k)
            match field["type"]:
                case Question.BOOLEAN_FIELD:
                    self.fields[key] = forms.BooleanField(required=False)
                case Question.INTEGER_FIELD:
                    self.fields[key] = forms.IntegerField(required=field["required"])
                case Question.DATETIME_FIELD:
                    self.fields[key] = forms.DateTimeField(
                        required=field["required"],
                        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
                    )
                case _:
                    self.fields[key] = forms.CharField(
                        required=field["required"],
                        max_length=4096,
                        widget=forms.Textarea(
                            attrs={"rows": 5, "placeholder": "Lorem Ipsum"}
                        ),
                    )

            self.fields[key].label = field["subject"]
            self.fields[key].help_text = field["description"]

    class Meta:
        model = Question  # TODO Replace by a model storing the filled in log.
        fields = ()
