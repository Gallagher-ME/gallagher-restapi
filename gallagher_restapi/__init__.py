"""Gallagher REST api library."""

from .client import CardholderClient, EventClient
from .exceptions import ConnectError, GllApiError, Unauthorized
from .models import EventFilter, FTAlarm, FTCardholder, FTEvent

MOVEMENT_EVENT_TYPES = ["20001", "20002", "20003", "20047", "20107", "42415"]

__all__ = [
    "CardholderClient",
    "EventClient",
    "EventFilter",
    "FTAlarm",
    "FTCardholder",
    "FTEvent",
    "ConnectError",
    "GllApiError",
    "Unauthorized",
]
