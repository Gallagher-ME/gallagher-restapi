"""Test Gallagher Events methods."""

from gallagher_restapi import Client
from gallagher_restapi import models


async def test_get_event(gll_client: Client) -> None:
    """Test getting events from Gallagher."""
    event_filter = models.EventQuery(
        top=10,
        previous=True,
        event_groups=[gll_client.event_groups["Access Denied"].id],
    )
    last_event = await gll_client.get_events(event_filter=event_filter)
    assert last_event
    assert last_event[0].message is not None


async def test_get_new_events(gll_client: Client) -> None:
    """Test getting new events from Gallagher."""
    event_filter = models.EventQuery(
        top=1,
        previous=True,
        event_groups=[gll_client.event_groups["Card Event"].id],
    )
    new_events, next = await gll_client.get_new_events(event_filter=event_filter)
    assert new_events
    assert next


async def test_yield_new_events(gll_client: Client) -> None:
    """Test yielding events from Gallagher."""
    event_filter = models.EventQuery(
        top=1,
        previous=True,
        event_groups=[gll_client.event_groups["Card Event"].id],
    )
    async for new_events in gll_client.yield_new_events(event_filter=event_filter):
        for event in new_events:
            assert event.message is not None
            break
        return


async def test_push_event(gll_client: Client) -> None:
    """Test pushing new event to Gallagher."""
    source = await gll_client.get_door(name="Dubai office")
    cardholders = await gll_client.get_cardholder(name="Rami Mousleh")
    assert cardholders[0].href
    assert source[0].href
    event_post = models.EventPost(
        event_type=gll_client.event_types["Key Returned"],
        source=models.FTItemReference(href=source[0].href),
        cardholder=models.FTItemReference(href=cardholders[0].href),
        message="A Key has been returned",
        details="Key number (123)",
    )
    event = await gll_client.push_event(event_post)
    assert event
    assert event.href is not None
