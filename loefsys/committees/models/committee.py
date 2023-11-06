from django.db import models
from loefsys.members.models import Member

from django.contrib.auth.models import User
from django.conf import settings


class Committee(models.Model):
    name = models.CharField(
        max_length=64,
    )

    shortname = models.CharField(
        max_length=20,
        null=True
    )

    members = models.ManyToManyField(
        to=Member,
        through="committees.CommitteeMembership",
        through_fields=("committee", "member"),
        symmetrical=True,
        blank=True,
    )

    @property
    def active_memberships(self):
        return self.committeemembership_set.filter(is_active=True)

    @property
    def head(self):
        return self.active_memberships.filter(is_head=True).user

    def __str__(self):
        return self.name
