"""Conftest for models tests."""

import json
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any

import httpx
import pytest
import pytest_asyncio
import respx

from gallagher_restapi import Client


@pytest.fixture(name="fixtures")
def mock_fixtures() -> dict[str, Any]:
    """Load and return the fixtures from tests/models/fixture.json once per session.

    Tests can accept a `fixtures` parameter and read entries by key, e.g.
    `payload = fixtures['FTApiFeatures']`.
    """
    path = Path(__file__).parent / "fixture.json"
    content = path.read_text(encoding="utf-8")
    return json.loads(content)


@pytest.fixture(autouse=True)
def respx_mock(fixtures: dict[str, Any]) -> Generator[respx.MockRouter, None, None]:
    """Mock the respx router."""
    api_features = fixtures["features"]
    with respx.mock(
        base_url="https://localhost:8904",
    ) as mock:
        mock.get("/api/").mock(
            return_value=httpx.Response(
                200, json={"features": api_features, "version": "9.30.123"}
            )
        )
        yield mock


@pytest_asyncio.fixture(name="gll_client")
async def gll_client() -> AsyncGenerator[Client]:
    """Return instance of Gallagher client."""
    client = Client("api_key")
    yield client
