"""Views for the member profiles."""

from typing import ClassVar

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.views.generic.detail import SingleObjectMixin


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
