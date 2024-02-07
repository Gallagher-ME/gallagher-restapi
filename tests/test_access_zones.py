"""Test getting the status of items."""
import asyncio
import pytest

from gallagher_restapi.client import Client


@pytest.mark.asyncio
async def test_get_access_zone(gll_client: Client) -> None:
    """Test getting an access zone item."""
    access_zones = await gll_client.get_access_zone()
    if access_zones:
        access_zone = await gll_client.get_access_zone(id=access_zones[0].id)
        assert access_zone[0].name is not None


@pytest.mark.asyncio
async def test_override_access_zone(gll_client: Client) -> None:
    """Test overriding an access zone item."""
    access_zones = await gll_client.get_access_zone()
    if access_zones:
        access_zone = await gll_client.get_access_zone(id=access_zones[0].id)
        assert access_zone[0].name is not None

        await gll_client.override_access_zone(access_zone[0].commands.secure)
        new_access_zone = await gll_client.get_access_zone(
            id=access_zone[0].id, extra_fields=["defaults", "statusFlags"]
        )
        assert new_access_zone[0].statusFlags == ["secure"]
