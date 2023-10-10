"""Gallagher REST api library."""

from .client import Client

from .exceptions import ConnectError, GllApiError, LicenseError, UnauthorizedError
from .models import EventFilter, EventPost, FTAlarm, FTCardholder, FTEvent

MOVEMENT_EVENT_TYPES = ["20001", "20002", "20003", "20047", "20107", "42415"]

__all__ = [
    "Client",
    "ConnectError",
    "EventFilter",
    "EventPost",
    "FTAlarm",
    "FTCardholder",
    "FTEvent",
    "GllApiError",
    "LicenseError",
    "UnauthorizedError",
]
