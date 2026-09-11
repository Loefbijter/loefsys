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
                    self.fields[key] = forms.BooleanField(
                        required=field["required"],
                        widget=forms.CheckboxInput(
                            attrs={
                                "class": (
                                    "h-4 w-4 rounded border-slate-300 text-secondary "
                                    "focus:ring-secondary"
                                )
                            }
                        ),
                    )
                case RegistrationFormField.INTEGER_FIELD:
                    self.fields[key] = forms.IntegerField(
                        required=field["required"],
                        widget=forms.NumberInput(
                            attrs={
                                "class": (
                                    "block w-full rounded-lg border border-slate-300 "
                                    "px-3 py-2.5 text-sm text-slate-900 shadow-sm "
                                    "transition "
                                    "focus:border-secondary "
                                    "focus:outline-none "
                                    "focus:ring-2 focus:ring-secondary/30"
                                )
                            }
                        ),
                    )
                case RegistrationFormField.DATETIME_FIELD:
                    self.fields[key] = forms.DateTimeField(
                        required=field["required"],
                        widget=forms.DateTimeInput(
                            attrs={
                                "type": "datetime-local",
                                "class": (
                                    "block w-full rounded-lg border border-slate-300 "
                                    "px-3 py-2.5 text-sm text-slate-900 shadow-sm "
                                    "transition "
                                    "focus:border-secondary "
                                    "focus:outline-none "
                                    "focus:ring-2 focus:ring-secondary/30"
                                ),
                            }
                        ),
                    )
                case _:  # RegistrationFormField.TEXT_FIELD
                    self.fields[key] = forms.CharField(
                        required=field["required"],
                        max_length=4096,
                        widget=forms.Textarea(
                            attrs={
                                "rows": 5,
                                "placeholder": "Typ hier je antwoord...",
                                "class": (
                                    "block w-full rounded-lg border border-slate-300 "
                                    "px-3 py-2.5 text-sm text-slate-900 shadow-sm "
                                    "transition "
                                    "focus:border-secondary "
                                    "focus:outline-none "
                                    "focus:ring-2 focus:ring-secondary/30"
                                ),
                            }
                        ),
                    )

            self.fields[key].label = field["subject"]
            self.fields[key].help_text = field["description"]
            self.fields[key].initial = (
                field["value"] if field["value"] is not None else field["default"]
            )

    def field_values(self):
        """Get field values."""
        for pk, field in self.form_fields:
            registration_form_field = RegistrationFormField.objects.get(id=pk)
            yield pk, self.cleaned_data.get(str(pk), registration_form_field.default)
