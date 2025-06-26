"""Module defining the forms for the reservations."""

from django import forms

from loefsys.members.models.user_skippership import UserSkippership
from loefsys.reservations.models.log import Question

from .models import ReservableItem, Reservation


class CreateReservationForm(forms.ModelForm):
    """A form to create reservations."""

    reserved_item = forms.ModelChoiceField(
        queryset=ReservableItem.objects.none(), widget=forms.RadioSelect
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

    authorized_userskippership = forms.ModelChoiceField(
        queryset=UserSkippership.objects.all(), required=False
    )

    class Meta:
        model = Reservation
        fields = ("reserved_item", "start", "end", "authorized_userskippership")


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
                            attrs={
                                "class": "w-full text-base p4 border border-gray-400 rounded-md",  # noqa ES01
                                "rows": 5,
                                "placeholder": "Lorem Ipsum",
                            }
                        ),
                    )

            self.fields[key].label = field["subject"]
            self.fields[key].help_text = field["description"]

    class Meta:
        model = Question  # TODO Replace by a model storing the filled in log.
        fields = ()
