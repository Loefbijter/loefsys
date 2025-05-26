"""Module defining the user account model for the website."""

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from loefsys.groups.models import LoefbijterGroup
from loefsys.users.models.name_mixin import NameMixin


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


class User(AbstractBaseUser, PermissionsMixin, NameMixin, TimeStampedModel):
    """The user model for authentication on the Loefbijter website.

    A user account can be made for two use cases. First, when a member registers at
    Loefbijter, an account is made for them as it is necessary for them to interact with
    loefsys for their membership. Additionally, it is also possible that a user account
    is made for guests who need access to the site. This user model is used for both
    cases and the only difference in model values is that a member has a

    Attributes
    ----------
    created : ~datetime.datetime
        The timestamp of the creation of this model.
    modified : ~datetime.datetime
        The timestamp of last modification of this model.
    email : str
        The email of the user, required to log in.
    password : str
        The password for this user.
    last_login : ~datetime.datetime
        the timestamp of the last login for this user.
    is_superuser : bool
        Designated that this user has all permissions without explicit assignation.
    groups : ~django.db.models.query.QuerySet of ~loefsys.groups.models.LoefbijterGroup
        The groups that this user belongs to.
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
    picture = models.ImageField(
        upload_to=user_picture_upload_path,
        null=True,
        blank=True,
        storage=OverwriteStorage(),
    )
    note = models.TextField(blank=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        return f"User {self.email}"
