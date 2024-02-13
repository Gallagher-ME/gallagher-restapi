"""Test Gallagher Events methods."""
import pytest

from gallagher_restapi.client import Client
from gallagher_restapi.models import EventPost, FTItemReference, EventFilter


@pytest.mark.asyncio
async def test_get_event(gll_client: Client) -> None:
    """Test getting events from Gallagher."""
    event_filter = EventFilter(
        top=10,
        previous=True,
        event_groups=[gll_client.event_groups["Access Denied"]],
    )
    last_event = await gll_client.get_events(event_filter=event_filter)
    assert last_event
    assert last_event[0].message is not None


@pytest.mark.asyncio
async def test_get_new_events(gll_client: Client) -> None:
    """Test getting new events from Gallagher."""
    event_filter = EventFilter(
        top=1,
        previous=True,
        event_groups=[gll_client.event_groups["Card Event"]],
    )
    new_events, next = await gll_client.get_new_events(event_filter=event_filter)
    assert new_events
    assert next


# @pytest.mark.asyncio
# async def test_yield_new_events(gll_client: Client) -> None:
#     """Test yielding events from Gallagher."""
#     event_filter = EventFilter(
#         top=1,
#         previous=True,
#         event_groups=[gll_client.event_groups["Card Event"]],
#     )
#     async for new_events in gll_client.yield_new_events(event_filter=event_filter):
#         for event in new_events:
#             assert event.message is not None
#             break


@pytest.mark.asyncio
async def test_push_event(gll_client: Client) -> None:
    """Test pushing new event to Gallagher."""
    source = await gll_client.get_door(name="Dubai office")
    cardholders = await gll_client.get_cardholder(name="Rami Mousleh")
    event_post = EventPost(
        eventType=gll_client.event_types["Key Returned"],
        source=FTItemReference(source[0].href),
        cardholder=FTItemReference(cardholders[0].href),
        message="A Key has been returned",
        details="Key number (123)",
    )
    event = await gll_client.push_event(event_post)
    assert event
    assert event.href is not None
