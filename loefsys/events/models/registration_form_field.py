"""
Defines the RegistrationForm model.

This model is used to handle registrations for events in the application.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from loefsys.events.models import event
from loefsys.events.models.registration import EventRegistration


class RegistrationFormField(models.Model):
    """
    Represents a registration form for events.

    This model stores the subject, response, and associated event for a registration.
    """

    BOOLEAN_FIELD = "boolean"
    INTEGER_FIELD = "integer"
    TEXT_FIELD = "text"
    DATETIME_FIELD = "datetime"

    FIELD_TYPES = [  # noqa: RUF012
        (BOOLEAN_FIELD, _("Boolean")),
        (INTEGER_FIELD, _("Integer")),
        (TEXT_FIELD, _("Text")),
        (DATETIME_FIELD, _("Datetime")),
    ]

    event = models.ForeignKey(event.Event, models.CASCADE, verbose_name=_("Event"))

    type = models.CharField(
        max_length=20, choices=FIELD_TYPES, default=TEXT_FIELD, verbose_name=_("Type")
    )

    subject = models.CharField(max_length=200, verbose_name=_("Subject"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    required = models.BooleanField(default=True, verbose_name=_("Required"))

    class Meta:
        order_with_respect_to = "event"

    def __str__(self):
        return self.subject

    @property
    def default(self):
        """Get default value for registration form field based on its type."""
        match self.type:
            case self.BOOLEAN_FIELD:
                return False
            case self.TEXT_FIELD:
                return ""
            case self.INTEGER_FIELD:
                return 0
            case self.DATETIME_FIELD:
                return None

    def __get_field_set(self):
        match self.type:
            case self.BOOLEAN_FIELD:
                return self.booleanregistrationinformation_set
            case self.TEXT_FIELD:
                return self.textregistrationinformation_set
            case self.INTEGER_FIELD:
                return self.integerregistrationinformation_set
            case self.DATETIME_FIELD:
                return self.datetimeregistrationinformation_set

    def get_value_for(self, registration):
        """Get value for registration form field based on registration."""
        value_set = self.__get_field_set()

        try:
            return value_set.get(registration=registration).value
        except (
            TextRegistrationInformation.DoesNotExist,
            BooleanRegistrationInformation.DoesNotExist,
            IntegerRegistrationInformation.DoesNotExist,
            DatetimeRegistrationInformation.DoesNotExist,
        ):
            return None

    def set_value_for(self, registration, value):
        """Set value for registration form field based on registration and value."""
        value_set = self.__get_field_set()

        try:
            field_value = value_set.get(registration=registration)
        except BooleanRegistrationInformation.DoesNotExist:
            field_value = BooleanRegistrationInformation()
        except TextRegistrationInformation.DoesNotExist:
            field_value = TextRegistrationInformation()
        except IntegerRegistrationInformation.DoesNotExist:
            field_value = IntegerRegistrationInformation()
        except DatetimeRegistrationInformation.DoesNotExist:
            field_value = DatetimeRegistrationInformation()

        field_value.registration = registration
        field_value.field = self
        field_value.value = value
        field_value.full_clean()
        field_value.save()


class AbstractRegistrationInformation(models.Model):
    """Abstract to contain common things for registration information."""

    registration = models.ForeignKey(EventRegistration, models.CASCADE)
    field = models.ForeignKey(RegistrationFormField, models.CASCADE)
    changed = models.DateTimeField(_("last changed"), auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.registration} - {self.field}: {self.value}"


class BooleanRegistrationInformation(AbstractRegistrationInformation):
    """Checkbox information filled in by members when registering."""

    value = models.BooleanField()


class TextRegistrationInformation(AbstractRegistrationInformation):
    """Checkbox information filled in by members when registering."""

    value = models.TextField(blank=True, default="", max_length=4096)


class IntegerRegistrationInformation(AbstractRegistrationInformation):
    """Checkbox information filled in by members when registering."""

    value = models.IntegerField()


class DatetimeRegistrationInformation(AbstractRegistrationInformation):
    """Checkbox information filled in by members when registering."""

    value = models.DateTimeField()
