"""Module defining the model for an address."""

from django.core import validators
from django.db import models
from django.db.models import OneToOneField
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from loefsys.contacts.models.contact import Contact


class Address(TimeStampedModel):
    """Model that defines an address.

    Attributes
    ----------
    created : ~datetime.datetime
        The timestamp of the creation of the model, automatically generated upon
        creation.
    modified : ~datetime.datetime
        The timestamp of last modification of this model, automatically generated upon
        update.
    contact : ~loefsys.contacts.models.contact.Contact
        The contact to whom the address details belongs.
    street : str
        The street and house number.
    street2 : str
        Additional information of the street if necessary.
    postal_code : str
        The postal code of the address.
    city : str
        The city that the address is located in.
    country : str
        The country that the city and address are located in.
    """

    contact = OneToOneField(to=Contact, on_delete=models.CASCADE, primary_key=True)

    street = models.CharField(
        max_length=100,
        validators=[
            validators.RegexValidator(
                regex=r"^.+ \d+.*", message=_("please use the format <street> <number>")
            )
        ],
        verbose_name=_("Street and house number"),
    )
    street2 = models.CharField(max_length=100, verbose_name=_("Second address line"))
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal code"))
    city = models.CharField(max_length=50, verbose_name=_("City"))
    country = models.CharField(max_length=50)  # TODO maybe change to django-countries
