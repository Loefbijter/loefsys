from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView


class UserProfileView(LoginRequiredMixin, DetailView):
    """View for displaying the profile of the logged-in user.
    
    overrides the get_object method to return the current user.
    """
    context_object_name = "member"
    model = get_user_model()
    template_name = "profiles/profile.html"

    def get_object(self, queryset=None):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        """Add user information to the context."""
        context = super().get_context_data(**kwargs)
        context["is_user_profile"] = True
        return context


class ProfileView(LoginRequiredMixin, DetailView):
    """View for displaying a user's profile by slug.

    Fetches the user based on the slug field. (user.slug)
    """
    context_object_name = "member"
    model = get_user_model()
    template_name = "profiles/profile.html"    
