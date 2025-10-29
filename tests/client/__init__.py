"""Tests for gallagher_restapi."""

from os import environ
from typing import Any

from gallagher_restapi import CloudGateway

cloud_gateway = None
if connection := environ.get("CLOUD_GATEWAY"):
    cloud_gateway = CloudGateway(connection)


CONFIG: dict[str, Any] = {
    "host": environ.get("HOST"),
    "port": environ.get("PORT"),
    "cloud_gateway": cloud_gateway,
    "api_key": environ.get("API_KEY"),
}
