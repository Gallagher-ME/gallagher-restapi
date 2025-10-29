"""Test getting the status of items."""

import pytest

from gallagher_restapi import Client


@pytest.mark.asyncio
async def test_get_access_zone(gll_client: Client) -> None:
    """Test getting an access zone item."""
    access_zones = await gll_client.get_access_zone()
    if access_zones:
        access_zone = await gll_client.get_access_zone(id=access_zones[0].id)
        assert access_zone[0].name is not None

    if divisions := await gll_client.get_item(item_types=["Division"], name="Test"):
        access_zone = await gll_client.get_access_zone(division=[divisions[0].id])
        assert len(access_zone) == 1


@pytest.mark.asyncio
async def test_override_access_zone(gll_client: Client) -> None:
    """Test overriding an access zone item."""
    access_zones = await gll_client.get_access_zone()
    if access_zones:
        access_zone = await gll_client.get_access_zone(id=access_zones[1].id)
        assert access_zone[0].name is not None
        assert access_zone[0].commands
        assert access_zone[0].commands.secure
        await gll_client.override_access_zone(access_zone[0].commands.secure)
        new_access_zone = await gll_client.get_access_zone(
            id=access_zone[0].id, extra_fields=["statusFlags"]
        )
        assert new_access_zone[0].statusFlags == ["secure"]
