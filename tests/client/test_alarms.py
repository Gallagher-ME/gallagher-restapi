"""Test Gallagher Events methods."""

import pytest

from gallagher_restapi import Client
from gallagher_restapi.models import FTAlarmState


@pytest.mark.asyncio
async def test_get_alarm(gll_client: Client) -> None:
    """Test getting alarms from Gallagher."""
    alarms = await gll_client.get_alarms()
    assert alarms
    assert alarms[0].message is not None
    assert isinstance(alarms[0].state, FTAlarmState)


@pytest.mark.asyncio
async def test_yield_alarms(gll_client: Client) -> None:
    """Test yielding alarms from Gallagher."""
    async for new_alarms in gll_client.yield_new_alarms():
        for alarm in new_alarms:
            assert alarm.message is not None
            break
        return


# @pytest.mark.asyncio
# async def test_alarm_action(gll_client: Client) -> None:
#     """Test pushing new event to Gallagher."""
#     source = await gll_client.get_door(name="Dubai office")
#     cardholders = await gll_client.get_cardholder(name="Rami Mousleh")
#     event_post = EventPost(
#         eventType=gll_client.event_types["Key Returned"],
#         source=FTItemReference(source[0].href),
#         cardholder=FTItemReference(cardholders[0].href),
#         message="A Key has been returned",
#         details="Key number (123)",
#     )
#     event = await gll_client.push_event(event_post)
#     assert event
#     assert event.href is not None
