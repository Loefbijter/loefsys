"""Views for the member profiles."""

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.views.generic.detail import SingleObjectMixin


class UserProfileMixin(SingleObjectMixin):
    """Mixin to retrieve the current user.

    Overrides the get_object method to return the current user.
    """

    def get_object(self, _queryset=None):
        """Retrieve the user from the request."""
        return self.request.user


class ProfileView(LoginRequiredMixin, DetailView):
    """View for displaying a user's profile by slug.

    Fetches the user based on the slug field. (user.slug)
    """

    context_object_name = "member"
    model = get_user_model()
    template_name = "profiles/profile.html"


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

    # Explicitly declare which fields are editable to avoid ImproperlyConfigured
    fields = [
        "first_name",
        "last_name",
        "initials",
        "nickname",
        "display_name_preference",
        "phone_number",
        "picture",
        "gender",
        "birthday",
        "show_birthday",
        "note",
    ]

    # After successful update, redirect to the user's own profile page
    success_url = reverse_lazy("members:user-profile")

    def get_context_data(self, **kwargs):
        """Provide the form as 'user_form' for the template and a placeholder 'member_form'."""
        context = super().get_context_data(**kwargs)
        # The UpdateView provides the ModelForm as 'form' in the context — the template expects 'user_form'
        context["user_form"] = context.get("form")
        # There is no separate 'member' form in this view; leave it None so the template can skip that section
        context["member_form"] = None
        # Mark that this is the logged-in user's profile (template may use this)
        context["is_user_profile"] = True
        return context
