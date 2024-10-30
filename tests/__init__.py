"""Tests for gallagher_restapi."""

from typing import Any

from gallagher_restapi.client import CloudGateway


CONFIG: dict[str, Any] = {
    "host": "localhost",
    "port": 8904,
    "cloud_gateway": CloudGateway.AU_GATEWAY,
    "api_key": "E2F5-F3EC-3F91-8DD8-AE52-0FE9-4B4F-26D5",
}
