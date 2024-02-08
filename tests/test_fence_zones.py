"""Test Gallagher Fence zones methods."""
import pytest

from gallagher_restapi.client import Client


@pytest.mark.asyncio
async def test_get_fence_zone(gll_client: Client) -> None:
    """Test getting a fence zone item."""
    fence_zones = await gll_client.get_fence_zone()
    if fence_zones:
        fence_zone = await gll_client.get_fence_zone(
            id=fence_zones[0].id, extra_fields=["defaults", "voltage"]
        )
        assert fence_zone[0].voltage
        assert fence_zone[0].voltage > 0


@pytest.mark.asyncio
async def test_override_fence_zone(gll_client: Client) -> None:
    """Test overriding a fence zone item."""
    if fence_zones := await gll_client.get_fence_zone(name="fence"):
        fence_zone = await gll_client.get_fence_zone(id=fence_zones[0].id)
        assert fence_zone[0].name is not None
        assert fence_zone[0].commands
        assert fence_zone[0].commands.off
        await gll_client.override_fence_zone(fence_zone[0].commands.off)
        new_fence_zone = await gll_client.get_fence_zone(
            id=fence_zone[0].id, extra_fields=["defaults", "statusFlags", "voltage"]
        )
        assert new_fence_zone[0].statusFlags == ["overridden", "off", "highVoltage"]
