"""Gallagher REST api python library."""
import asyncio
import logging
from enum import Enum
from ssl import SSLError
from typing import Any, AsyncIterator

import httpx

from .exceptions import (
    ConnectError,
    GllApiError,
    LicenseError,
    RequestError,
    Unauthorized,
)
from .models import (
    EventFilter,
    FTApiFeatures,
    FTCardholder,
    FTEvent,
    FTEventGroup,
    FTItem,
    FTItemReference,
    FTITemTypes,
    FTPersonalDataFieldDefinition,
)

_LOGGER = logging.getLogger(__name__)


class Client:
    """Gallagher REST api base client."""

    api_features: FTApiFeatures
    item_types: FTITemTypes

    def __init__(
        self,
        api_key: str,
        *,
        host: str = "localhost",
        port: int = 8904,
        httpx_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize REST api client."""
        self.server_url = f"https://{host}:{port}"
        self.httpx_client: httpx.AsyncClient = httpx_client or httpx.AsyncClient(
            verify=False
        )
        self.httpx_client.headers = httpx.Headers(
            {
                "Authorization": f"GGL-API-KEY {api_key}",
                "Content-Type": "application/json",
            }
        )
        self.httpx_client.timeout.read = 60
        self.event_groups: dict[str, FTEventGroup] = {}
        self.event_types: dict[str, FTItem] = {}

    async def _async_request(
        self,
        method: str,
        endpoint: str,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, str] | str | None = None,
    ) -> Any:
        """Send a http request and return the response."""
        _LOGGER.info(
            "Sending %s request to endpoint: %s, data: %s, params: %s",
            method,
            endpoint,
            data,
            params,
        )
        try:
            response = await self.httpx_client.request(
                method, endpoint, params=params, json=data
            )
        except (httpx.ConnectError, httpx.ReadTimeout, SSLError) as err:
            raise ConnectError(
                f"Connection failed while sending request: {err}"
            ) from err
        _LOGGER.debug(
            "status_code: %s, response: %s", response.status_code, response.text
        )
        if response.status_code == httpx.codes.UNAUTHORIZED:
            raise Unauthorized("Unauthorized request. Ensure api key is correct")
        if response.status_code == httpx.codes.FORBIDDEN:
            raise LicenseError("Site is not licensed for this operation")
        if response.status_code == httpx.codes.NOT_FOUND:
            raise RequestError(
                "Requested item does not exist or "
                "your operator does not have the privilege to view it"
            )
        if response.status_code == httpx.codes.BAD_REQUEST:
            raise RequestError(response.json()["message"])
        if response.status_code in [httpx.codes.CREATED, httpx.codes.NO_CONTENT]:
            return True
        return response.json()

    async def authenticate(self) -> None:
        """Connect to Server to authenticate."""
        response = await self._async_request("GET", f"{self.server_url}/api/")
        self.api_features = FTApiFeatures(**response["features"])

    async def get_item_types(self) -> None:
        """Get FTItem types."""
        item_types: list[str] = []
        response = await self._async_request(
            "GET", self.api_features.href("items/itemTypes")
        )
        if response.get("itemTypes"):
            item_types = [
                item_type["name"]
                for item_type in response["itemTypes"]
                if item_type["name"]
            ]
        self.item_types = Enum("FTITemTypes", item_types)  # type: ignore

    async def get_item(
        self, item_type: FTITemTypes, name: str | None = None
    ) -> list[FTItem]:
        """Get FTItems filtered by type and name."""
        # We will force selecting type for now
        params = {"type": item_type.value}
        if name:
            params["name"] = name
        items: list[FTItem] = []
        if response := await self._async_request(
            "GET", self.api_features.href("items"), params=params
        ):
            items = [FTItem(**item) for item in response["results"]]
        return items

    async def get_personal_data_field(
        self, name: str | None = None, extra_fields: list[str] = []
    ) -> list[FTItem]:
        """Return List of available personal data fields."""
        pdfs: list[FTItem] = []
        params = {}
        if name:
            params["name"] = name
        if extra_fields:
            params["fields"] = ",".join(extra_fields)

        if response := await self._async_request(
            "GET", self.api_features.href("personalDataFields"), params=params
        ):
            pdfs = [
                FTPersonalDataFieldDefinition.from_dict(pdf)
                for pdf in response["results"]
            ]

        return pdfs

    async def get_cardholder(
        self,
        *,
        id: int | None = None,
        name: str | None = None,
        pdfs: dict[str, str] | None = None,
        extra_fields: list[str] = [],
    ) -> list[FTCardholder]:
        """Return list of cardholders."""
        cardholders: list[FTCardholder] = []
        if id:
            response: dict[str, Any] = await self._async_request(
                "GET", f"{self.api_features.href('cardholders')}/{id}"
            )
            if response:
                return [FTCardholder.from_dict(response)]

        else:
            if name and not isinstance(name, str):
                raise ValueError("name field must be a string value.")
            if pdfs and not isinstance(pdfs, dict):
                raise ValueError("pdfs field must be a dict.")
            params = {}
            if name:
                params = {"name": name}

            if pdfs:
                for pdf_name, value in pdfs.items():
                    if not (pdf_name.startswith('"') and pdf_name.endswith('"')):
                        pdf_name = f'"{pdf_name}"'
                    # if pdf name is correct we expect the result to include one item only
                    if not (
                        pdf_field := await self.get_personal_data_field(name=pdf_name)
                    ):
                        raise GllApiError(f"pdf field: {pdf_name} not found")
                    params.update({f"pdf_{pdf_field[0].id}": value})

            if extra_fields:
                params["fields"] = ",".join(extra_fields)

            response = await self._async_request(
                "GET", self.api_features.href("cardholders"), params=params
            )
            if response["results"]:
                cardholders = [
                    FTCardholder.from_dict(cardholder)
                    for cardholder in response["results"]
                ]
        return cardholders

    async def add_cardholder(self, cardholder: FTCardholder) -> FTItemReference:
        """Add a new cardholder in Gallagher."""
        return await self._async_request(
            "POST", self.api_features.href("cardholders"), data=cardholder.as_dict
        )

    async def update_cardholder(self, cardholder: FTCardholder) -> bool:
        """Update existing cardholder in Gallagher."""
        return await self._async_request(
            "PATCH",
            cardholder.href,
            data=cardholder.as_dict,
        )

    async def remove_cardholder(self, cardholder: FTCardholder) -> bool:
        """Remove existing cardholder in Gallagher."""
        return await self._async_request(
            "DELETE",
            cardholder.href,
        )

    async def get_event_types(self) -> None:
        """Return list of event types."""
        response = await self._async_request(
            "GET", self.api_features.href("events/eventGroups")
        )
        self.event_groups = {
            FTEventGroup.from_dict(event_group).name: FTEventGroup.from_dict(
                event_group
            )
            for event_group in response["eventGroups"]
        }
        for event_group in self.event_groups.values():
            self.event_types.update(
                {event_type.name: event_type for event_type in event_group.event_types}
            )

    async def get_events(
        self, event_filter: EventFilter | None = None
    ) -> list[FTEvent]:
        """Return list of events filtered by params."""
        events: list[FTEvent] = []
        if response := await self._async_request(
            "GET",
            self.api_features.href("events"),
            params=event_filter.as_dict if event_filter else None,
        ):
            events = [FTEvent.from_dict(event) for event in response["events"]]
        return events

    async def get_new_events(
        self, event_filter: EventFilter | None = None
    ) -> AsyncIterator[list[FTEvent]]:
        """Yield a list of new events filtered by params."""
        response = await self._async_request(
            "GET",
            self.api_features.href("events/updates"),
            params=event_filter.as_dict if event_filter else None,
        )
        while True:
            _LOGGER.debug(response)
            yield [FTEvent.from_dict(event) for event in response["events"]]
            await asyncio.sleep(1)
            response = await self._async_request(
                "GET",
                response["updates"]["href"],
                params=event_filter.as_dict if event_filter else None,
            )
