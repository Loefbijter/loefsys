from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from .membership import Membership


class User(AbstractBaseUser, PermissionsMixin):
    contact = models.OneToOneField(
        to="Contact",
        on_delete=models.CASCADE,
        null=False,
        verbose_name=_("User contact"),
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    membership_set: QuerySet["Membership"]

    def __str__(self):
        return self.contact.email
