from django.db import models
from django.utils.translation import gettext_lazy as _

from .group import Group


class Committee(Group):
    mandatory = models.BooleanField(
        default=False,
        help_text=_(
            "If this is checked new members should be assigned to this committee, any members that are part of this "
            "committee satisfy their committee_duty."
        ),
    )
