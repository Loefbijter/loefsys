"""Module defining the views for user accounts."""

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, View
from django.views.generic.edit import FormView

from loefsys.members.models import MemberDetails
from loefsys.members.models.membership import Membership

from . import forms
from .forms import SignupForm

User = get_user_model()


class ProfileLoginView(LoginView):
    """View for logging in users."""

    next_page = "/profile"


class ProfileSignupView(FormView):
    """View for signing up users."""

    template_name = "registration/signup.html"
    form_class = SignupForm
    success_url = "/profile/login/"

    def form_valid(self, form):
        """On valid credentials save the sign up data."""
        form.save()
        return super().form_valid(form)


class ProfilePasswordResetView(PasswordResetView):
    """View for requesting password reset."""

    template_name = "password_reset/request_password_reset.html"
    email_template_name = "password_reset/reset_password_email.html"  # email body
    subject_template_name = (
        "password_reset/reset_password_subject.txt"  # email subject line
    )
    success_url = "/profile/password-reset/done/"


class ProfilePasswordResetDoneView(PasswordResetDoneView):
    """View for confirmation page after reseting password."""

    template_name = "password_reset/password_reset_done.html"


class ProfilePasswordResetCompleteView(PasswordResetCompleteView):
    """View for when password reset has been completed."""

    template_name = "password_reset/password_reset_complete.html"


class ProfilePasswordResetConfirmView(PasswordResetConfirmView):
    """View for entering a new password."""

    template_name = "password_reset/password_reset_confirm.html"
    success_url = "/profile/password-reset/complete/"


class SignupFormView(FormView):
    """Sign up page view."""

    template_name = "registration/signup.html"
    form_class = SignupForm
    success_url = "/"

    def form_valid(self, form):
        """Save the new user and log them in after a successful registration."""
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class AccountinfoView(LoginRequiredMixin, View):
    """Account information view."""

    template_name = "account_info/accountinfopage.html"

    def get_account_info(self):
        """Get account information from the user."""
        user_info = {
            "name": self.request.user.display_name.strip(),
            "email": self.request.user.email,
            "phone_number": self.request.user.phone_number,
            "picture": self.request.user.picture,
            "groups": self.request.user.groups.all(),
        }
        member_info = []
        qs_member = MemberDetails.objects.filter(user=self.request.user)
        if qs_member.count() == 1:
            member = qs_member[0]
            qs_membership = Membership.objects.filter(member=member)
            if qs_membership.count() > 0:
                membership = qs_membership[::-1][0]
                member_info = {
                    "birthday": member.birthday.__str__(),
                    "show_birthday": member.show_birthday,
                    "member_since": membership.start.__str__(),
                    "activities": "",
                }
            else:
                raise Exception("Member has no membership")
        return user_info, member_info

    def get(self, request):
        """Handle the get request for the account information page."""
        user_info, member_info = self.get_account_info()

        return render(
            request,
            self.template_name,
            {"user_info": user_info, "member_info": member_info},
        )


class AccountinfoeditView(LoginRequiredMixin, View):
    """Account information edit view."""

    template_name = "account_info/accountinfoeditpage.html"

    def get(self, request):
        """Handle the get request for the edit account information form."""
        user_form = forms.EditUserInfo(instance=self.request.user)
        member_list = MemberDetails.objects.filter(user=self.request.user)
        member_form = (
            forms.EditMemberInfo(instance=member_list[0])
            if member_list.count() > 0
            else None
        )
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "member_form": member_form},
        )

    def post(self, request):
        """Handle the post request for the edit account information form."""
        old_picture = self.request.user.picture

        user_form = forms.EditUserInfo(
            request.POST, request.FILES, instance=self.request.user
        )
        member_list = MemberDetails.objects.filter(user=self.request.user)
        member_form = (
            forms.EditMemberInfo(request.POST, request.FILES, instance=member_list[0])
            if member_list.count() > 0
            else None
        )
        if user_form.is_valid() and (member_form is None or member_form.is_valid()):
            if not user_form.cleaned_data.get("picture") and old_picture:
                # Delete the old profile picture from storage
                old_picture.delete(save=False)
            user_form.save()
            if member_form is not None:
                member_form.save()
            return redirect("accountinfo")
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "member_form": member_form},
        )


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    """Delete the account of the currently logged-in user."""

    model = User
    template_name = "account_info/confirm_account_delete.html"
    success_url = reverse_lazy("login")

    def get_object(self):
        """Only allow users to delete their own account."""
        return self.request.user

    def delete(self, request):
        """Override to log out user before deleting."""
        user = self.get_object()
        logout(request)
        user.delete()
        return redirect(self.success_url)
