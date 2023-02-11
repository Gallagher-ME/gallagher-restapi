import argparse
import asyncio
import logging

import httpx

import gallagher_restapi

_LOGGER = logging.getLogger(__name__)


async def main(host: str, port: int, api_key: str) -> None:
    """Test connecting to Gallagher REST api."""
    try:
        async with httpx.AsyncClient(verify=False) as httpx_client:
            cardholder_client = gallagher_restapi.CardholderClient(
                host=host,
                port=port,
                api_key=api_key,
                httpx_client=httpx_client,
            )
            await cardholder_client.authenticate()
            if cardholders := await cardholder_client.get_cardholder():
                _LOGGER.info(
                    "Successfully connected to Gallagher server"
                    "and retrieved %s cardholders",
                    len(cardholders),
                )
    except gallagher_restapi.GllApiError as err:
        _LOGGER.error(err)
    try:
        async with httpx.AsyncClient(verify=False) as httpx_client:
            event_client = gallagher_restapi.EventClient(
                host=host,
                port=port,
                api_key=api_key,
                httpx_client=httpx_client,
            )
            await event_client.authenticate()
            event_filter = gallagher_restapi.EventFilter(
                top=1,
                previous=True,
            )
            last_event = await event_client.get_events(filter=event_filter)
            _LOGGER.info(
                "Successfully connected to Gallagher server "
                "and retrieved the last event: %s",
                last_event[0].message,
            )
    except gallagher_restapi.GllApiError as err:
        _LOGGER.error(err)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("api_key", type=str)
    parser.add_argument("host", type=str, default="localhost")
    parser.add_argument("-p", "--port", type=int, default=8904)
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
