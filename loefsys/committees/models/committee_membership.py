from django.db import models
from loefsys.members.models import Member

from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class CommitteeMembership(models.Model):
    member = models.ForeignKey(
        Member,
        models.CASCADE,
    )

    committee = models.ForeignKey(
        "committees.Committee",
        models.CASCADE,
    )

    is_head = models.BooleanField(
        default=False,
    )

    since = models.DateField()

    until = models.DateField(
        null=True,
        blank=True,
    )

    note = models.CharField(
        max_length=256,
        blank=True,
    )

    @property
    def is_active(self):
        return self.until is None or self.since > timezone.now() > self.until

    def __str__(self):
        return str(self.committee) + " | " + str(self.member)
