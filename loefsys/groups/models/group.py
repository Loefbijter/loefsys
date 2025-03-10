"""Module defining the generic group model."""

from django.contrib.auth.models import Permission
from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class GroupManager[TGroup: "LoefbijterGroup"](models.Manager[TGroup]):
    """Custom manager for group models.

    The manager is used by models inheriting the
    :class:`~loefsys.groups.models.group.LoefbijterGroup` model.

    """

    use_in_migrations = True

    def get_by_natural_key(self, name):
        """Get an instance by its natural key."""
        return self.get(name=name)


class LoefbijterGroup(TimeStampedModel):
    """Describes a group of members.

    Groups are a generic way of categorizing users to apply permissions, or
    some other label, to those users. A user can belong to any number of
    groups.

    This model represents a group within Loefbijter. Subclasses exist for specific
    groups, such as boards or committees, but the generic model is also available. This
    model mirrors the behaviour of the internal Django Groups model as it provides an
    easy way of managing permissions.

    Attributes
    ----------
    name : str
        The name of the group.
    description : str
        A description of the group.
    permissions : ~django.db.models.query.QuerySet or \
        ~django.contrib.auth.models.Permission
        The permissions for this group.
    date_foundation : ~datetime.date
        The date that the group was founded on.
    date_discontinuation : ~datetime.date, None
        The date that the group ceased to exist.
        Cannot be before date_foundation.
    display_members : bool
        A flag that determines whether the members of the group are publicly visible.

    Properties
    ----------
    active :
        A property that returns whether the group is currently active.

        It is calculated by whether :attr:`.date_discontinuation` exists and whether
        the date has passed.
    """

    name = models.CharField(_("Name"), max_length=150, unique=True)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    permissions = models.ManyToManyField(
        Permission, verbose_name=_("Permissions"), blank=True
    )
    date_foundation = models.DateField(_("Date of foundation"))
    date_discontinuation = models.DateField(
        _("Date of discontinuation"), blank=True, null=True
    )

    class Meta:
        constraints = (
            CheckConstraint(
                name="date_discontinuation_gte_date_foundation",
                condition=Q(date_discontinuation__gte=models.F("date_foundation")),
                violation_error_message=_(
                    "The date of discontinuation can't be before the date of foundation"
                ),
            ),
        )

    @property
    def active(self):
        """Return whether the group is currently active."""
        return (
            self.date_discontinuation is None or
            self.date_discontinuation >= now().__str__()
        )

    display_members = models.BooleanField(_("Display group members"))

    objects = GroupManager()

    def __str__(self):
        return f"Group {self.name}"

    def natural_key(self):
        """Return the natural key for a group."""
        return (self.name,)
