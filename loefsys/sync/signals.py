"""Module for registring signals for user-related models."""

from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from loefsys.users.models import (
    Address,
    MemberDetails,
    Membership,
    StudyRegistration,
    User,
)

from .tasks import sync_all_services


@receiver(post_save, sender=User)
def on_user_save(*, instance, **_):
    """Create a MemberDetails instance when a User is created."""
    sync_all_services.delay_on_commit(instance.pk)


@receiver(post_save, sender=MemberDetails)
def on_member_details_save(*, instance, **_):
    """Create a Membership instance when a MemberDetails is created."""
    sync_all_services.delay_on_commit(instance.user.pk)


@receiver(post_save, sender=Membership)
def on_membership_save(*, instance, **_):
    """Create a Membership instance when a MemberDetails is created."""
    sync_all_services.delay_on_commit(instance.member.user.pk)


@receiver(post_save, sender=StudyRegistration)
def on_study_registration_save(instance, **_):
    """Create a Membership instance when a StudyRegistration is created."""
    sync_all_services.delay_on_commit(instance.member.user.pk)


@receiver(post_save, sender=Address)
def on_address_save(instance, **_):
    """Create a Membership instance when an Address is created."""
    if hasattr(instance, "memberdetails"):
        sync_all_services.delay_on_commit(instance.memberdetails.user.pk)
