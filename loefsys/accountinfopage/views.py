"""Module defining the views for accountinfopage."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import View

from loefsys.members.models import MemberDetails
from loefsys.members.models.membership import Membership

from . import forms


class AccountinfoView(LoginRequiredMixin, View):
    """Account information view."""

    template_name = "accountinfopage.html"
    login_url = "signup"

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

    template_name = "accountinfoeditpage.html"
    login_url = "signup"

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
