"""Module defining the room reservable model."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .reservable import ReservableItem


class Room(ReservableItem):
    """Model defining a room that can be reserved.

    A room is a place the Loefbijter owns which can be used by any part within
    Loefbijter (this does not include the VvS). It has a limited capacity and has
    required permission.

    Attributes
    ----------
    capacity : int
        The capacity of the room.
    """

    capacity = models.PositiveSmallIntegerField(verbose_name=_("Capacity"))
