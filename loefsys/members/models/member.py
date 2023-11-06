from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core import validators

from django.db.models import Value, Q
from django.db.models.functions import Concat

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField
from localflavor.generic.models import IBANField

from ...utils import countries


class PaymentMethods(models.TextChoices):
    COLLECTION = "IN", _("Collection")


class Genders(models.TextChoices):
    MALE = "M", _("Male")
    FEMALE = "F", _("Female")
    OTHER = "O", _("Other")
    UNSPECIFIED = "U", _("Prefer not to say")


class Member(models.Model):
    # connect conscribo member to user
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    relation_number = models.PositiveIntegerField(
        primary_key=True,
    )

    first_name = models.CharField(
        max_length=64,
        verbose_name=_("First name"),
        default="",
        blank=False,
    )

    last_name = models.CharField(
        max_length=64,
        default="",
        verbose_name=_("Last name"),
        blank=False,
    )

    # ----- Registration information -----

    institution = models.CharField(
        max_length=20,
        verbose_name=_("Educational institution"),
        blank=True,
    )

    programme = models.CharField(
        max_length=20,
        verbose_name=_("Study programme"),
        blank=True,
    )

    student_number = models.CharField(
        verbose_name=_("Student number"),
        max_length=8,
        validators=[
            validators.RegexValidator(
                regex=r"(s\d{7}|[ezu]\d{6,7})",
                message=_("Enter a valid student- or e/z/u-number."),
            )
        ],
        blank=True,
        unique=True,
    )

    RSC_number = models.CharField(
        verbose_name=_("RSC card number"),
        max_length=9,
        blank=True,
        unique=True,
    )

    member_since = models.DateField()

    member_until = models.DateField(null=True, blank=True)

    alumni_since = models.DateField(blank=True, null=True)

    payment_method = models.CharField(
        choices=PaymentMethods.choices,
        max_length=2,
    )

    remark = models.TextField(
        max_length=500,
        blank=True,
    )

    # ---- Address information -----

    address_street = models.CharField(
        max_length=100,
        validators=[
            validators.RegexValidator(
                regex=r"^.+ \d+.*",
                message=_("please use the format <street> <number>"),
            )
        ],
        verbose_name=_("Street and house number"),
        null=True,
    )

    address_street2 = models.CharField(
        max_length=100,
        verbose_name=_("Second address line"),
        blank=True,
        null=True,
    )

    address_postal_code = models.CharField(
        max_length=10,
        verbose_name=_("Postal code"),
        null=True,
    )

    address_city = models.CharField(
        max_length=40,
        verbose_name=_("City"),
        null=True,
    )

    address_country = models.CharField(
        max_length=2,
        choices=countries.EUROPE,
        verbose_name=_("Country"),
        null=True,
    )

    # ---- Personal information ------

    phone_number = PhoneNumberField()

    IBAN = IBANField()

    birthday = models.DateField(verbose_name=_("Birthday"), null=True)

    gender = models.CharField(
        choices=Genders.choices,
        max_length=1,
    )

    # --- Communication preference ----

    receive_newsletter = models.BooleanField(
        verbose_name=_("Receive newsletter"),
        help_text=_("Receive the Newsletter"),
        default=True,
    )

    # ___________________________-

    # # TODO dependency: pillow
    # avatar = models.ImageField(
    #     upload_to=None,
    #     blank=True,
    #     null=True,
    # )

    show_birthday = models.BooleanField(
        verbose_name=_("Display birthday"),
        help_text=_(
            "Show your birthday to other members on your profile page and "
            "in the birthday calendar"
        ),
        default=True,
    )

    profile_description = models.TextField(
        verbose_name=_("Profile text"),
        help_text=_("Text to display on your profile"),
        blank=True,
        max_length=4096,
    )

    initials = models.CharField(
        max_length=20,
        verbose_name=_("Initials"),
        blank=True,
        null=True,
    )

    nickname = models.CharField(
        max_length=30,
        verbose_name=_("Nickname"),
        blank=True,
        null=True,
    )

    display_name_preference = models.CharField(
        max_length=10,
        verbose_name=_("How to display name"),
        choices=(
            ("full", _("Show full name")),
            ("nickname", _("Show only nickname")),
            ("firstname", _("Show only first name")),
            ("initials", _("Show initials and last name")),
            ("fullnick", _("Show name like \"John 'nickname' Doe\"")),
            ("nicklast", _("Show nickname and last name")),
        ),
        default="full",
    )

    @property
    def is_member(self):
        return self.member_until > timezone.now().date()

    # @property
    # def active_committees(self):
    #     return self.committees.filter(committeemembership__until=None)
    #
    # @admin.display(
    #     boolean=True,
    #     description=_('Committee Head'),
    # )
    # def is_committee_head(self):
    #     return self.active_committees\
    #                .filter(Q(committeemembership__is_head=True))\
    #                .exists()

    # @property
    # @admin.display(ordering=Concat('last_name', Value(' '), 'first_name'))
    # def full_name(self):
    #     return self.user.get_full_name()

    def __str__(self):
        return self.first_name + " " + self.last_name
