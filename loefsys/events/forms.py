"""Module defining the forms for events."""

from django import forms

from .models import RegistrationFormField


class EventFieldsForm(forms.Form):
    """Form for all fields associated with an event."""

    def __init__(self, *args, **kwargs):
        self.form_fields = kwargs.pop("form_fields")
        super().__init__(*args, **kwargs)

        for k, field in self.form_fields:
            key = str(k)
            match field["type"]:
                case RegistrationFormField.BOOLEAN_FIELD:
                    self.fields[key] = forms.BooleanField(required=False)
                case RegistrationFormField.INTEGER_FIELD:
                    self.fields[key] = forms.IntegerField(required=field["required"])
                case RegistrationFormField.DATETIME_FIELD:
                    self.fields[key] = forms.DateTimeField(
                        required=field["required"],
                        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
                    )
                case _:  # RegistrationFormField.TEXT_FIELD
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
            self.fields[key].initial = (
                field["value"] if field["value"] else field["default"]
            )

    def field_values(self):
        """Get field values."""
        for pk, field in self.form_fields:
            registration_form_field = RegistrationFormField.objects.get(id=pk)
            yield pk, self.cleaned_data.get(str(pk), registration_form_field.default)
