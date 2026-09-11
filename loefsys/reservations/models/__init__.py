"""Module defining models for the reservations app."""

from .boat import ReservableBoat
from .logbook import BoatDamageRecord, BoatLogbook
from .material import ReservableMaterial
from .reservable import Reservable, ReservableType
from .reservation import Reservation
from .room import ReservableRoom

__all__ = [
    "BoatDamageRecord",
    "BoatLogbook",
    "Reservable",
    "ReservableBoat",
    "ReservableMaterial",
    "ReservableRoom",
    "ReservableType",
    "Reservation",
]
