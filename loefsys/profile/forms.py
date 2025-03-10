"""A forms module to handle input for the sign up page."""

from django.contrib.auth.forms import UserCreationForm

from loefsys.users.models.user import User


class SignupForm(UserCreationForm):
    """Sign up Form for email and password."""

    class Meta:
        model = User
        fields = ("email",)
