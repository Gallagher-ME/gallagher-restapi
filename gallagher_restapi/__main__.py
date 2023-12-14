"""cli interface for gallagher restapi."""
import argparse
import asyncio
from datetime import datetime
import logging
import os

import httpx

import gallagher_restapi
from gallagher_restapi.models import FTAccessGroupMembership, FTCardholder

_LOGGER = logging.getLogger(__name__)


async def main(host: str, port: int, api_key: str) -> None:
    """Test connecting to Gallagher REST api."""
    try:
        async with httpx.AsyncClient(verify=False) as httpx_client:
            client = gallagher_restapi.Client(
                host=host,
                port=port,
                api_key=api_key,
                httpx_client=httpx_client,
            )
            await client.initialize()
            if divisions := await client.get_item(item_type="Division", name="Test"):
                access_group = await client.get_access_group(
                    divisions=[divisions[0].id]
                )

                _LOGGER.info(access_group)
            if cardholders := await client.get_cardholder(id="1366"):
                cardholder = cardholders[0]
                assert isinstance(cardholder.accessGroups, list)
                cardholder_accessGroups = [
                    group
                    for group in cardholder.accessGroups
                    if group.accessGroup.name == "Test"
                ]
                access_group_memebership = FTAccessGroupMembership.update_membership(
                    cardholder_accessGroups[0], active_until=datetime(2024, 1, 1)
                )
                new_membership = FTAccessGroupMembership.add_membership(access_group[0])

                cardholder_update = FTCardholder.patch(
                    cardholder=cardholder,
                    add=[new_membership],
                    update=[access_group_memebership],
                    remove=[cardholder_accessGroups[-1]],
                )
                await client.update_cardholder(cardholder_update)
                _LOGGER.info(f"Successfully updated cardholder {cardholder.firstName}")
    except gallagher_restapi.GllApiError as err:
        _LOGGER.error(f"Error: {err}")
    try:
        async with httpx.AsyncClient(verify=False) as httpx_client:
            client = gallagher_restapi.Client(
                host=host,
                port=port,
                api_key=api_key,
                httpx_client=httpx_client,
            )
            await client.initialize()
            if cardholders := await client.get_cardholder(
                extra_fields=["id", "firstName", "lastName"]
            ):
                _LOGGER.info(
                    "Successfully connected to Gallagher server"
                    "and retrieved %s cardholders",
                    len(cardholders),
                )
    except gallagher_restapi.GllApiError as err:
        _LOGGER.error(err)
    try:
        async with httpx.AsyncClient(verify=False) as httpx_client:
            client = gallagher_restapi.Client(
                host=host,
                port=port,
                api_key=api_key,
                httpx_client=httpx_client,
            )
            await client.initialize()
            event_filter = gallagher_restapi.EventFilter(
                top=1,
                previous=True,
                event_groups=[client.event_groups["Card Event"]],
            )
            last_event = await client.get_events(event_filter=event_filter)
            _LOGGER.info(
                "Successfully connected to Gallagher server "
                "and retrieved the last event: %s",
                last_event[0].message,
            )
    except gallagher_restapi.GllApiError as err:
        _LOGGER.error(err)
    try:
        async with httpx.AsyncClient(verify=False) as httpx_client:
            client = gallagher_restapi.Client(
                host=host,
                port=port,
                api_key=api_key,
                httpx_client=httpx_client,
            )
            await client.initialize()
            source = await client.get_door(name="Dubai office")
            cardholders = await client.get_cardholder(name="Rami Mousleh")
            event_post = gallagher_restapi.EventPost(
                eventType=client.event_types["Key Returned"],
                source=source[0],
                cardholder=cardholders[0],
                message="A Key has been returned",
                details="Key number (123)",
            )
            event = await client.push_event(event_post)
            _LOGGER.info(
                "Successfully connected to Gallagher server "
                "and pushed new event: %s",
                event,
            )
    except gallagher_restapi.GllApiError as err:
        _LOGGER.error(err)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-api_key", help="Gallagher API Key", type=str, default=os.getenv("API_KEY")
    )
    parser.add_argument("-host", type=str, default=os.getenv("HOST") or "localhost")
    parser.add_argument("-p", "--port", type=int, default=os.getenv("PORT") or 8904)
    parser.add_argument("-D", "--debug", action="store_true")
    args = parser.parse_args()

    LOG_LEVEL = logging.INFO
    if args.debug:
        LOG_LEVEL = logging.DEBUG
    logging.basicConfig(format="%(message)s", level=LOG_LEVEL)

    try:
        asyncio.run(main(host=args.host, port=args.port, api_key=args.api_key))
    except KeyboardInterrupt:
        pass
