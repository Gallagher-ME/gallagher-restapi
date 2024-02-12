"""Test getting the status of items."""
import pytest

from gallagher_restapi.client import Client


@pytest.mark.asyncio
async def test_get_alarm_zone(gll_client: Client) -> None:
    """Test getting an alam zone item."""
    alarm_zones = await gll_client.get_alarm_zone()
    if alarm_zones:
        alarm_zone = await gll_client.get_alarm_zone(id=alarm_zones[0].id)
        assert alarm_zone[0].name is not None


@pytest.mark.asyncio
async def test_override_alarm_zone(gll_client: Client) -> None:
    """Test overriding an alarm zone item."""
    if alarm_zones := await gll_client.get_alarm_zone(name="fence"):
        alarm_zone = await gll_client.get_alarm_zone(id=alarm_zones[0].id)
        assert alarm_zone[0].name is not None
        assert alarm_zone[0].commands
        assert alarm_zone[0].commands.armLowFeel
        await gll_client.override_alarm_zone(alarm_zone[0].commands.armLowFeel)
        new_alarm_zone = await gll_client.get_alarm_zone(
            id=alarm_zone[0].id, extra_fields=["statusFlags"]
        )
        assert new_alarm_zone[0].statusFlags == ["armed", "lowFeel"]
