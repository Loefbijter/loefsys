from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ActiveMemberGroupManager(models.Manager):
    """Returns active objects only sorted by the localized name."""

    def get_queryset(self):
        return super().get_queryset().exclude(active=False).order_by("name")


class Group(models.Model):
    """Describes a group of members (Users with Membership object)."""

    class GroupTypes(models.IntegerChoices):
        BOARD = 1, _("Board")
        COMMITTEE = 2, _("Committee")
        SOCIETY = 3, _("Society")
        FRATERNITY = 4, _("Fraternity")
        YEARCLUB = 5, _("Yearclub")

    group_type = models.SmallIntegerField(
        verbose_name=_("Group Type"),
        choices=GroupTypes.choices,
    )

    # objects = models.Manager()
    # active_objects = ActiveMemberGroupManager()

    name = models.CharField(max_length=40, verbose_name=_("Groupname"), unique=True)

    description = models.TextField()

    # photo = models.ImageField(
    #     verbose_name=_("Image"),
    #     upload_to="committeephotos/",
    #     storage=get_public_storage,
    #     null=True,
    #     blank=True,
    # )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="groups.GroupMembership",
    )

    # permissions = models.ManyToManyField(
    #     Permission,
    #     verbose_name=_("permissions"),
    #     blank=True,
    # )

    active = models.BooleanField(
        default=False,
        help_text=_("This should only be unchecked if the group has been dissolved."),
    )

    contact_email = models.EmailField(
        _("contact email address"),
        blank=True,
        null=True,
    )

    # contact_mailinglist = models.OneToOneField(
    #     "mailinglists.MailingList",
    #     verbose_name=_("contact mailing list"),
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    # )

    display_members = models.BooleanField(
        default=False,
    )

    since = models.DateField(
        _("founded in"),
        null=True,
        blank=True,
    )

    until = models.DateField(
        _("existed until"),
        null=True,
        blank=True,
    )

    @property
    def size(self):
        return self.members.count()

    def __str__(self):
        return str(self.name)

    # def get_absolute_url(self):
    #     try:
    #         return self.board.get_absolute_url()
    #     except self.DoesNotExist:
    #         try:
    #             return self.committee.get_absolute_url()
    #         except self.DoesNotExist:
    #             try:
    #                 return self.society.get_absolute_url()
    #             except self.DoesNotExist:
    #                 # pylint: disable=raise-missing-from
    #                 raise NotImplementedError(
    #                     f"get_absolute_url() not implemented for {self.__class__.__name__}"
    #                 )
