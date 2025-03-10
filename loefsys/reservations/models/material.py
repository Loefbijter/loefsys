"""Module defining the model for generic materials."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .reservable import ReservableItem


class Material(ReservableItem):
    """Describes a material item that can be reserved.

    A gear-piece is any wearable item used for sailing. It is of a type and has a size
    measure.

    Attributes
    ----------
    size : str
        The size of the item (if applicable?).
    """

    size = models.CharField(max_length=10, verbose_name=_("Size"))
