"""Module defining the user account model for the website."""

from typing import TYPE_CHECKING, Optional

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import OneToOneField, QuerySet
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import RandomCharField
from phonenumber_field.modelfields import PhoneNumberField

from loefsys.groups.models import LoefbijterGroup
from loefsys.members.models.choices import DisplayNamePreferences

from .address import Address
from .choices import Genders

if TYPE_CHECKING:
    from .membership import Membership
    from .study_registration import StudyRegistration


class UserManager(BaseUserManager):
    """Manager for the User model.

    Basically a copy of the regular UserManager, but without the username.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given email and password."""
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class OverwriteStorage(FileSystemStorage):
    """Custom storage class that overwrites files with the same name.

    Needed because when a user uploads a new profile picture, the old
    one would otherwise still be present together with the new one that
    gets renamed.
    """

    def get_available_name(self, name, max_length=None):  # noqa: ARG002
        """Given the desired name, derive and return a name that is available."""
        if self.exists(name):
            self.delete(name)
        return name


class User(
    AbstractBaseUser,
    TimeStampedModel,
    PermissionsMixin,
):
    """The user model for authentication on the Loefbijter website.

    A user account can be made for two use cases. First, when a member registers at
    Loefbijter, an account is made for them as it is necessary for them to interact with
    loefsys for their membership. Additionally, it is also possible that a user account
    is made for guests who need access to the site. This user model is used for both
    cases and the only difference in model values is that a member has a

    Attributes
    ----------
    created : ~datetime.datetime
        The timestamp of the creation of this model. Inherited from TimestampedModel.
    modified : ~datetime.datetime
        The timestamp of last modification of this model.

        Inherited from TimestampedModel.

    password : str
        The password for this user.

        Inherited from AbstractBaseUser.

    last_login : ~datetime.datetime
        the timestamp of the last login for this user.

        Inherited from AbstractBaseUser.



    is_superuser : bool
        Flag that determines whether the user has all permissions
        without explicitly assigned

        Inheristed from PermissionsMixin.

    groups : ~django.db.models.query.QuerySet of ~loefsys.groups.models.LoefbijterGroup
        The groups that this user belongs to.

        Inherited from PermissionsMixin.d.    email : str
        The email of the user, used to log in. This value is unique.
    is_staff : bool
        Flag that determines whether has access to the admin site.
    first_name : str
        The first name of the user.

    is_active : bool
        Flag that determines whether the member can log in with their account.
    last_name : str
        The last name of the user.
    initials : str
        The initials of the user.
    is_superuser : bool
        Designated that this user
    nickname : str
        The nickname of the user, or blank if not applicable.
    display_name_preference :  has all permissions without explicit assignation.
    groups : ~django.db.models.query.QuerySet of ~loefsys.groups.models.LoefbijterGroup
        The groups that this  ~loefsys.users.models.choices.DisplayNamePreference
        The user's preference of how they want their name to be displayed.


    er belongs to.
    user_permissions : ~django.db.models.query.QuerySet of \
        ~django.contrib.auth.models.Permission
        The specific permissions for this user.
    phone_number : str
        The phone number of the user.

        For members, a phone number is required, and it is recommended for guest
        accounts too. However, it is possible that no phone number is available for
        ex-members, so the field should take into account empty values too.
    picture : ~django.db.models.fields.files.ImageFieldFile
    note : str
        A note field that are only visible to active board members.

        For guest accounts, a note can provide information for which purpose this
        account exists. For members, incidents can potentially be tracked.
    """

    def user_upload_directory(self):
        """Return the user upload directory."""
        return f"user_{self.id}"

    def user_picture_upload_path(self, _):
        """Return the upload path for the user profile picture."""
        return self.user_upload_directory() + "/picture.jpg"

    def delete_profile_picture(self):
        """Delete the image file associated with the profile picture."""
        if self.picture:
            self.picture.delete(save=False)

    email = models.EmailField(unique=True)

    slug = RandomCharField(length=8, unique=True)

    is_staff = models.BooleanField(
        _("Staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Designates whether this user should be treated as active."),
    )

    first_name = models.CharField(max_length=64, verbose_name=_("First name"))
    last_name = models.CharField(max_length=64, verbose_name=_("Last name"))

    initials = models.CharField(max_length=20, verbose_name=_("Initials"), blank=True)
    nickname = models.CharField(max_length=30, verbose_name=_("Nickname"), blank=True)

    display_name_preference = models.PositiveSmallIntegerField(
        choices=DisplayNamePreferences, default=DisplayNamePreferences.FULL
    )

    picture = models.ImageField(
        upload_to=user_picture_upload_path,
        null=True,
        blank=True,
        storage=OverwriteStorage(),
    )

    gender = models.PositiveSmallIntegerField(choices=Genders, verbose_name=_("Gender"), default=Genders.UNSPECIFIED)

    birthday = models.DateField(verbose_name=_("Birthday"), null=True, blank=True)
    show_birthday = models.BooleanField(verbose_name=_("Display birthday"), default=False)

    address = OneToOneField(to=Address, on_delete=models.SET_NULL, null=True)

    study_registration: Optional["StudyRegistration"]
    membership_set: QuerySet["Membership"]

    # Copied from PermissionsMixin to override Group type to LoefbijterGroup.
    groups = models.ManyToManyField(
        LoefbijterGroup,
        verbose_name=_("Groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="user_set",
        related_query_name="user",
    )

    phone_number = PhoneNumberField(blank=True)

    # TODO: Refactor
    note = models.TextField(blank=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    objects = UserManager()

    @property
    def full_name(self) -> str:
        """Return the full name of the person."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self) -> str:
        """Return the display name of the user based on their preference."""
        match self.display_name_preference:
            case DisplayNamePreferences.FULL_WITH_NICKNAME:
                return f"{self.first_name} '{self.nickname}' {self.last_name}".strip()
            case DisplayNamePreferences.NICKNAME_LASTNAME:
                return f"'{self.nickname}' {self.last_name}".strip()
            case DisplayNamePreferences.INITIALS_LASTNAME:
                return f"{self.initials} {self.last_name}".strip()
            case DisplayNamePreferences.FIRSTNAME_ONLY:
                return self.first_name.strip()
            case _:
                return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        """Meta options for the User model."""

        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("modified",)

    def __str__(self):
        return f"User {self.email}"
