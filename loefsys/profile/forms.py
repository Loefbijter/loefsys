"""A forms module to handle input for the sign up page."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import PhoneNumberField

from loefsys.members.models import MemberDetails, User


class SignupForm(UserCreationForm):
    """Form for signing up."""

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = PhoneNumberField(required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password1",
            "password2",
        )

    def clean_first_name(self):  # noqa: D102
        first_name = self.cleaned_data["first_name"]
        return first_name.capitalize()

    def clean_last_name(self):  # noqa: D102
        last_name = self.cleaned_data["last_name"]
        return last_name.capitalize()


class EditUserInfo(forms.ModelForm):
    """Form for editing user info."""

    class Meta:
        model = User
        fields = ("phone_number", "nickname", "display_name_preference", "picture")


class EditMemberInfo(forms.ModelForm):
    """Form for editing member info."""

    class Meta:
        model = MemberDetails
        fields = ("gender", "birthday", "show_birthday")
