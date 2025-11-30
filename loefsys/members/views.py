"""Views for the member profiles."""

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
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


class UserProfileEditView(UserProfileMixin, UpdateView):
    """View for updating the profile of the logged-in user."""

    context_object_name = "member"
    model = get_user_model()
    template_name = "profiles/profile_edit.html"
