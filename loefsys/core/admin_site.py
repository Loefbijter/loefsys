"""Admin site where access follows from a user's permissions."""

from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


def can_access_admin(user) -> bool:
    """Return whether ``user`` may log in to the admin site.

    Staff members always can. Other users can as soon as they hold any permission,
    for example through a group, so there's no need to also mark them as staff.
    """
    if not user.is_active:
        return False
    return user.is_staff or bool(user.get_all_permissions())


class PermissionAdminAuthenticationForm(AdminAuthenticationForm):
    """Admin login form that accepts every user who may access the admin."""

    def confirm_login_allowed(self, user):
        """Reject users who have neither staff status nor any permission."""
        AuthenticationForm.confirm_login_allowed(self, user)
        if not can_access_admin(user):
            raise ValidationError(
                self.error_messages["invalid_login"],
                code="invalid_login",
                params={"username": self.username_field.verbose_name},
            )


class LoefsysAdminSite(admin.AdminSite):
    """Admin site that admits users based on their permissions."""

    login_form = PermissionAdminAuthenticationForm

    def has_permission(self, request):
        """Return whether the user of ``request`` may access the admin site."""
        return can_access_admin(request.user)
