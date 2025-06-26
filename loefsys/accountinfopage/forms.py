"""Module defining the forms for accountinfopage."""

from django import forms

from loefsys.members.models import MemberDetails, User


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
