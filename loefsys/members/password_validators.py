"""Adds some extra requirements for creating a password."""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomComplexityValidator:
    """Defines some regular expressions that need to be in the password."""

    def validate(self, password, __):
        """Validate regular expressions that need to be in the password."""
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter.")
            )
        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("The password must contain at least one lowercase letter.")
            )
        if not re.search(r"\d", password):
            raise ValidationError(_("The password must contain at least one digit."))
        if not re.search(r"[^\w\s]", password):
            raise ValidationError(
                _("The password must contain at least one special character.")
            )

    def get_help_text(self):
        """Return a message if the requirements are not met."""
        return _(
            "The password must contain at least one uppercase letter, one lowercase "
            "letter, one digit and one special character."
        )
