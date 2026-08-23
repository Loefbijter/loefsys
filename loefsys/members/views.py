"""Views for the member profiles."""

import logging
from typing import ClassVar

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import DetailView, FormView, TemplateView, UpdateView
from django.views.generic.detail import SingleObjectMixin

logger = logging.getLogger(__name__)


class UserProfileEditForm(forms.ModelForm):
    """Profile form with a Dutch-friendly birthday format."""

    birthday = forms.DateField(
        required=False,
        input_formats=["%d-%m-%Y", "%Y-%m-%d"],
        widget=forms.TextInput(
            attrs={
                "placeholder": "dd-mm-jjjj",
                "inputmode": "numeric",
                "autocomplete": "bday",
                "maxlength": "10",
                "pattern": r"\d{2}-\d{2}-\d{4}",
            }
        ),
    )

    class Meta:
        """Configure editable user fields."""

        model = get_user_model()
        fields: ClassVar[list[str]] = [
            "first_name",
            "last_name",
            "initials",
            "nickname",
            "display_name_preference",
            "phone_number",
            "pod_kb_link",
            "pod_zb_link",
            "picture",
            "gender",
            "birthday",
            "show_birthday",
            "note",
        ]


class UserProfileMixin(SingleObjectMixin):
    """Mixin to retrieve the current user.

    Overrides the get_object method to return the current user.
    """

    def get_object(self, _queryset=None):
        """Retrieve the user from the request."""
        return self.request.user


def _is_ancestor_of(skippership, ancestor):
    """Return whether ``ancestor`` is part of the parent chain for ``skippership``."""
    current = skippership
    while current is not None:
        if current.pk == ancestor.pk:
            return True
        current = current.parent
    return False


class ProfileView(LoginRequiredMixin, DetailView):
    """View for displaying a user's profile by slug.

    Fetches the user based on the slug field. (user.slug)
    """

    context_object_name = "member"
    model = get_user_model()
    template_name = "profiles/profile.html"

    def get_context_data(self, **kwargs):
        """Add a filtered list of skipperships to the profile context.

        Only the furthest-child skipperships are shown: if the user has both KB1 and KB2
        and KB1 is an ancestor of KB2, only KB2 is included in display_skipperships.
        """
        context = super().get_context_data(**kwargs)
        member = self.get_object()
        entries = list(member.user_skipperships.select_related("skippership"))
        display = []
        for entry in entries:
            if any(
                _is_ancestor_of(other.skippership, entry.skippership)
                for other in entries
                if other.skippership_id != entry.skippership_id
            ):
                continue
            display.append(entry.skippership)
        context["display_skipperships"] = display
        return context


class UserProfileView(UserProfileMixin, ProfileView):
    """View for displaying the profile of the logged-in user.

    Overrides the get_object method to return the current user.
    """

    def get_context_data(self, **kwargs):
        """Add user information to the context."""
        context = super().get_context_data(**kwargs)
        context["is_user_profile"] = True
        return context


class UserProfileEditView(LoginRequiredMixin, UserProfileMixin, UpdateView):
    """View for updating the profile of the logged-in user."""

    context_object_name = "member"
    model = get_user_model()
    template_name = "profiles/profile_edit.html"
    form_class = UserProfileEditForm

    # After successful update, redirect to the user's own profile page
    success_url = reverse_lazy("members:user-profile")

    def get_context_data(self, **kwargs):
        """Provide the form as 'user_form' for the template.

        The template also expects a 'member_form' key — set it to None here so the
        template can skip rendering that section when it's not present.
        """
        context = super().get_context_data(**kwargs)
        # The UpdateView provides the ModelForm as 'form' in the context — the
        # template expects it under 'user_form'.
        context["user_form"] = context.get("form")
        # There is no separate 'member' form in this view; leave it None so the
        # template can skip that section.
        context["member_form"] = None
        # Mark that this is the logged-in user's profile (template may use this)
        context["is_user_profile"] = True
        return context


class UserSetPasswordView(LoginRequiredMixin, FormView):
    """Allow a logged-in user to set a new password without providing the old one.

    Uses Django's SetPasswordForm which validates the two password fields
    and applies the configured password validators.
    """

    template_name = "profiles/set_password.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("members:user-profile")

    def get_form(self, form_class=None):
        """Instantiate the SetPasswordForm with the current user.

        Django's SetPasswordForm expects the user as a positional argument
        (user, *args, **kwargs). Instantiate it directly to avoid passing
        ``user`` as a kwarg which breaks BaseModelForm initialisation.
        """
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        """Save the new password and keep the user logged in."""
        form.save()
        # Keep the user logged in after password change
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, "Wachtwoord succesvol bijgewerkt.")
        return super().form_valid(form)


class PasswordResetByEmailForm(forms.Form):
    """Simple form asking for the user's email address."""

    email = forms.EmailField(label="E-mailadres")


class PasswordResetByEmailView(FormView):
    """Let a user request a temporary password by entering their email.

    If the email corresponds to a user account, generate a temporary password,
    set it on the user, save, and email the temporary password to the user.

    The response page is the same whether or not an account was found to avoid
    leaking which emails are registered.
    """

    template_name = "registration/password_reset_form.html"
    form_class = PasswordResetByEmailForm
    success_url = reverse_lazy("members:reset-password-done")

    def form_valid(self, form):
        """Process the password-reset form and email temporary passwords.

        The success response is shown regardless of whether an account was
        found to avoid leaking registered addresses.
        """
        email = form.cleaned_data["email"].strip()
        user_model = get_user_model()
        users = user_model.objects.filter(email__iexact=email)

        # Always show success page, but only send email if user exists.
        if users.exists():
            for user in users:
                # Generate a reasonably strong temporary password
                temp_password = get_random_string(12)
                user.set_password(temp_password)
                user.save()

                # Send the temporary password via email using the project's template
                subject = "Tijdelijk wachtwoord - Loefsys"
                from_email = (
                    getattr(settings, "DEFAULT_FROM_EMAIL", None)
                    or getattr(settings, "SERVER_EMAIL", None)
                    or "no-reply@example.com"
                )
                context = {
                    "user": user,
                    "temp_password": temp_password,
                    "protocol": self.request.scheme,
                    "domain": self.request.get_host(),
                }
                message = render_to_string(
                    "registration/password_reset_email.html", context
                )
                try:
                    send_mail(
                        subject, message, from_email, [user.email], fail_silently=False
                    )
                    # If using the file backend, log where the file should be written
                    logger.info(
                        "Password reset email sent to %s (backend=%s)",
                        user.email,
                        getattr(settings, "EMAIL_BACKEND", ""),
                    )
                except Exception:
                    # Log the error so failures are visible during development/ops.
                    # Still show the generic success page to the user.
                    logger.exception(
                        "Failed to send password reset email to %s", user.email
                    )

        messages.success(
            self.request,
            (
                "Als het opgegeven e-mailadres bestaat, is er een tijdelijk "
                "wachtwoord gestuurd."
            ),
        )
        return super().form_valid(form)


class PasswordResetDoneView(TemplateView):
    """Page shown after a password-reset request is processed."""

    template_name = "registration/password_reset_done.html"
