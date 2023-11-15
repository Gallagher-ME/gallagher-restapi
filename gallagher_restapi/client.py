"""Gallagher REST api python library."""
import asyncio
import logging
from ssl import SSLError
from typing import Any, AsyncIterator

import httpx

from awesomeversion import AwesomeVersion
from .exceptions import (
    ConnectError,
    GllApiError,
    LicenseError,
    RequestError,
    UnauthorizedError,
)
from .models import (
    DoorSort,
    EventFilter,
    FTApiFeatures,
    FTCardholder,
    FTDoor,
    FTEvent,
    FTEventGroup,
    EventPost,
    FTItem,
    FTItemReference,
    FTPersonalDataFieldDefinition,
)

_LOGGER = logging.getLogger(__name__)


class Client:
    """Gallagher REST api base client."""

    api_features: FTApiFeatures

    def __init__(
        self,
        api_key: str,
        *,
        host: str = "localhost",
        port: int = 8904,
        token: str | None = None,
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
        if token:
            self.httpx_client.headers["IntegrationLicense"] = token
        self.httpx_client.timeout.read = 60
        self._item_types: dict[str, str] = {}
        self.event_groups: dict[str, FTEventGroup] = {}
        self.event_types: dict[str, FTItem] = {}
        self.version: str | None = None

    async def _async_request(
        self,
        method: str,
        endpoint: str,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        extra_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Send a http request and return the response."""
        params = params or {}
        if extra_fields:
            params["fields"] = ",".join(extra_fields)

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
        except (httpx.RequestError, SSLError) as err:
            raise ConnectError(
                f"Connection failed while sending request: {err}"
            ) from err
        _LOGGER.debug(
            "status_code: %s, response: %s", response.status_code, response.text
        )
        if response.status_code == httpx.codes.UNAUTHORIZED:
            raise UnauthorizedError("Unauthorized request. Ensure api key is correct")
        if response.status_code == httpx.codes.FORBIDDEN:
            raise LicenseError("Site is not licensed for this operation")
        if response.status_code == httpx.codes.NOT_FOUND:
            raise RequestError(
                "Requested item does not exist or "
                "your operator does not have the privilege to view it"
            )
        if response.status_code == httpx.codes.BAD_REQUEST:
            raise RequestError(response.json()["message"])
        if response.status_code == httpx.codes.CREATED:
            return {"location": response.headers.get("location")}
        if response.status_code == httpx.codes.NO_CONTENT:
            return {}
        return response.json()

    async def initialize(self) -> None:
        """Connect to Server and initialize data."""
        response = await self._async_request("GET", f"{self.server_url}/api/")
        self.api_features = FTApiFeatures(**response["features"])
        self.version = AwesomeVersion(response["version"])
        await self._update_item_types()
        await self._update_event_types()

    async def _update_item_types(self) -> None:
        """Get FTItem types."""
        response = await self._async_request(
            "GET", self.api_features.href("items/itemTypes")
        )
        if response.get("itemTypes"):
            self._item_types = {
                item_type["name"]: item_type["id"]
                for item_type in response["itemTypes"]
                if item_type["name"]
            }

    async def get_item(
        self,
        item_type: str,
        name: str | None = None,
        extra_fields: list[str] | None = None,
    ) -> list[FTItem]:
        """Get FTItems filtered by type and name."""
        # We will force selecting type for now
        if not (type_id := self._item_types.get(item_type)):
            raise ValueError(f"Unknown item type: {item_type}")
        params = {"type": type_id}
        if name:
            params["name"] = name
        items: list[FTItem] = []
        if response := await self._async_request(
            "GET",
            self.api_features.href("items"),
            params=params,
            extra_fields=extra_fields,
        ):
            items = [FTItem(**item) for item in response["results"]]
        return items

    async def get_access_zone(
        self,
        name: str | None = None,
        extra_fields: list[str] | None = None,
    ) -> list[FTItem]:
        """Get Access zones filtered by name."""
        params: dict[str, str] = {}
        if name:
            params["name"] = name
        items: list[FTItem] = []
        if response := await self._async_request(
            "GET",
            self.api_features.href("access_zones"),
            params=params,
            extra_fields=extra_fields,
        ):
            items = [FTItem(**item) for item in response["results"]]
        return items

    async def get_access_group(
        self,
        name: str | None = None,
        extra_fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get Access groups filtered by name."""
        params: dict[str, str] = {}
        if name:
            params["name"] = name
        # items: list[FTItem] = []
        response = await self._async_request(
            "GET",
            self.api_features.href("access_groups"),
            params=params,
            extra_fields=extra_fields,
        )
        # items = [FTItem(**item) for item in response["results"]]
        return response["results"]

    # Door methods
    async def get_door(
        self,
        *,
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        sort: DoorSort = DoorSort.ID_ASC,
        divisions: list[FTItem] = [],
        extra_fields: list[str] | None = None,
    ) -> list[FTDoor]:
        """Return list of doors."""
        doors: list[FTDoor] = []
        if id:
            response: dict[str, Any] = await self._async_request(
                "GET", f"{self.api_features.href('doors')}/{id}"
            )
            if response:
                return [FTDoor.from_dict(response)]

        else:
            params: dict[str, Any] = {"sort": sort}
            if name:
                params["name"] = name
            if description:
                params["description"] = description
            if divisions:
                params["divisions"] = ",".join(div.id for div in divisions)

            response = await self._async_request(
                "GET",
                self.api_features.href("doors"),
                params=params,
                extra_fields=extra_fields,
            )
            if response["results"]:
                doors = [FTDoor.from_dict(door) for door in response["results"]]
        return doors

    # Personal fields methods
    async def get_personal_data_field(
        self,
        name: str | None = None,
        extra_fields: list[str] | None = None,
    ) -> list[FTPersonalDataFieldDefinition]:
        """Return List of available personal data fields."""
        pdfs: list[FTPersonalDataFieldDefinition] = []
        params = {}
        if name:
            params["name"] = name

        if response := await self._async_request(
            "GET",
            self.api_features.href("personalDataFields"),
            params=params,
            extra_fields=extra_fields,
        ):
            pdfs = [
                FTPersonalDataFieldDefinition.from_dict(pdf)
                for pdf in response["results"]
            ]

        return pdfs

    # Cardholder methods
    async def get_cardholder(
        self,
        *,
        id: int | None = None,
        name: str | None = None,
        pdfs: dict[str, str] | None = None,
        extra_fields: list[str] | None = None,
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
                    # if pdf name is correct the result should include one item only
                    if not (
                        pdf_field := await self.get_personal_data_field(name=pdf_name)
                    ):
                        raise GllApiError(f"pdf field: {pdf_name} not found")
                    params.update({f"pdf_{pdf_field[0].id}": value})

            response = await self._async_request(
                "GET",
                self.api_features.href("cardholders"),
                params=params,
                extra_fields=extra_fields,
            )
            if response["results"]:
                cardholders = [
                    FTCardholder.from_dict(cardholder)
                    for cardholder in response["results"]
                ]
        return cardholders

    async def add_cardholder(self, cardholder: FTCardholder) -> FTItemReference:
        """Add a new cardholder in Gallagher."""
        response = await self._async_request(
            "POST", self.api_features.href("cardholders"), data=cardholder.as_dict()
        )
        return FTItemReference(response["location"])

    async def update_cardholder(self, cardholder: FTCardholder) -> dict[str, Any]:
        """Update existing cardholder in Gallagher."""
        return await self._async_request(
            "PATCH",
            cardholder.href,
            data=cardholder.as_dict(),
        )

    async def remove_cardholder(self, cardholder: FTCardholder) -> None:
        """Remove existing cardholder in Gallagher."""
        await self._async_request(
            "DELETE",
            cardholder.href,
        )

    # Event methods
    async def _update_event_types(self) -> None:
        """Fetch list of event groups and types from server."""
        response = await self._async_request(
            "GET", self.api_features.href("events/eventGroups")
        )

        for item in response["eventGroups"]:
            event_group = FTEventGroup.from_dict(item)
            self.event_groups[event_group.name] = event_group

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
            params=event_filter.as_dict() if event_filter else None,
        ):
            events = [FTEvent.from_dict(event) for event in response["events"]]
        return events

    async def get_new_events(
        self,
        event_filter: EventFilter | None = None,
        updates: str | None = None,
    ) -> tuple[list[FTEvent], str]:
        """
        Return new events filtered by params and the link for the next event search.
        """
        if updates is not None:
            response = await self._async_request(
                "GET",
                updates,
            )
        else:
            response = await self._async_request(
                "GET",
                self.api_features.href("events"),
                params=event_filter.as_dict() if event_filter else None,
            )
        events: list[FTEvent] = [
            FTEvent.from_dict(event) for event in response["events"]
        ]
        next: str = response["next"]["href"]
        return (events, next)

    async def yield_new_events(
        self, event_filter: EventFilter | None = None
    ) -> AsyncIterator[list[FTEvent]]:
        """Yield a list of new events filtered by params."""
        response = await self._async_request(
            "GET",
            self.api_features.href("events/updates"),
            params=event_filter.as_dict() if event_filter else None,
        )
        while True:
            _LOGGER.debug(response)
            yield [FTEvent.from_dict(event) for event in response["events"]]
            await asyncio.sleep(1)
            # Check if next link should be called,
            # how to tell if there are more events in next link
            response = await self._async_request(
                "GET",
                response["updates"]["href"],
                params=event_filter.as_dict() if event_filter else None,
            )

    async def push_event(self, event: EventPost) -> FTItemReference | None:
        """Push a new event to Gallagher and return the event href."""
        response = await self._async_request(
            "POST", self.api_features.href("events"), data=event.as_dict()
        )
        if href := response.get("location"):
            return href
        return None
