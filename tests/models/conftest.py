"""Conftest for models tests."""

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def fixtures() -> dict:
    """Load and return the fixtures from tests/models/fixture.json once per module.

    Tests can accept a `fixtures` parameter and read entries by key, e.g.
    `payload = fixtures['FTApiFeatures']`.
    """
    path = Path(__file__).parent / "fixture.json"
    content = path.read_text(encoding="utf-8")
    return json.loads(content)
