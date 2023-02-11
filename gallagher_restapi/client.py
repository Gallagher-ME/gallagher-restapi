"""Gallagher REST api python library."""
import asyncio
import logging
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
    FTEventType,
    FTItem,
)

_LOGGER = logging.getLogger(__name__)


class BaseClient:
    """Gallagher REST api base client."""

    api_features: FTApiFeatures
    item_types: dict

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
            {"Authorization": f"GGL-API-KEY {api_key}"}
        )
        self.httpx_client.timeout.read = 60

    async def _async_request(
        self, method: str, endpoint: str, params: dict[str, str] | None = None
    ) -> Any:
        """Send a http request and return the response."""
        _LOGGER.info("Sending request to endpoint: %s, params: %s", endpoint, params)
        try:
            response = await self.httpx_client.request(method, endpoint, params=params)
        except (httpx.ConnectError, httpx.ReadTimeout, SSLError) as err:
            raise ConnectError(
                f"Connection failed while sending request: {err}"
            ) from err
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
        if response.status_code != httpx.codes.OK:
            raise GllApiError(response.text)
        _LOGGER.debug("Response: %s", response.text)
        return response.json()

    async def authenticate(self):
        """Connect to Server to authenticate."""
        response = await self._async_request("GET", f"{self.server_url}/api/")
        self.api_features = FTApiFeatures(response["features"])

    async def get_item_types(self):
        """Get FTItem types."""
        item_types = await self._async_request("GET", self.api_features.item_types.href)
        if item_types.get("itemTypes"):
            for item_type in item_types["itemTypes"]:
                self.item_types.update({item_type["name"]: item_type["id"]})


class CardholderClient(BaseClient):
    """REST api cardholder client for Gallagher Command Center."""

    async def get_personal_data_field(self, name: str | None = None) -> list[FTItem]:
        """Return List of available personal data fields."""
        pdfs: list[FTItem] = []
        params = {}
        if name:
            params = {"name": name}

        if response := await self._async_request(
            "GET", self.api_features.personal_data_fields.href, params=params
        ):
            pdfs = [FTItem(pdf) for pdf in response]

        return pdfs

    async def get_cardholder(
        self,
        *,
        ftitem_id: int | None = None,
        name: str | None = None,
        pdfs: dict[str, str] | None = None,
        detailed: bool = False,
    ) -> list[FTCardholder]:
        """Return list of cardholders."""
        cardholders: list[FTCardholder] = []
        if ftitem_id:
            response: dict[str, Any] = await self._async_request(
                "GET", f"{self.api_features.cardholders.href}/{ftitem_id}"
            )
            if response:
                return [FTCardholder(response)]

        else:
            if name and not isinstance(name, str):
                raise ValueError("name field must be a string value.")
            if pdfs and not isinstance(pdfs, dict):
                raise ValueError("pdfs field must be a dict.")
            params = {}
            if name:
                params = {"name": name}

            if pdfs:
                for name, value in pdfs.items():
                    if not (name.startswith('"') and name.endswith('"')):
                        name = f'"{name}"'
                    # if pdf name is correct we expect the result to include one item only
                    if not (pdf_field := await self.get_personal_data_field(name=name)):
                        raise GllApiError(f"pdf field: {name} not found")
                    params.update({f"pdf_{pdf_field[0].ftitem_id}": value})

            response = await self._async_request(
                "GET", self.api_features.cardholders.href, params=params
            )
            if response["results"]:
                if detailed:
                    for cardholder in response["results"]:
                        cardholder_details = await self._async_request(
                            "GET", cardholder["href"]
                        )
                        cardholders.append(FTCardholder(cardholder_details))
                else:
                    cardholders = [
                        FTCardholder(cardholder) for cardholder in response["results"]
                    ]
        return cardholders


class EventClient(BaseClient):
    """REST api event client for Gallagher Command Center."""

    event_groups: dict[str, FTEventGroup]
    event_types: dict[str, FTEventType]

    async def get_event_types(self) -> None:
        """Return list of event types."""
        response = await self._async_request(
            "GET", self.api_features.events_features.event_groups.href
        )
        self.event_groups = {
            FTEventGroup(event_group).name: FTEventGroup(event_group)
            for event_group in response["eventGroups"]
        }
        self.event_types = {}
        for event_group in self.event_groups.values():
            self.event_types.update(
                {event_type.name: event_type for event_type in event_group.event_types}
            )

    async def get_events(self, filter: EventFilter | None = None) -> list[FTEvent]:
        """Return list of events filtered by params."""
        events: list[FTEvent] = []
        if response := await self._async_request(
            "GET",
            self.api_features.events_features.events.href,
            params=filter.params if filter else None,
        ):
            events = [FTEvent(event) for event in response["events"]]
        return events

    async def get_new_events(
        self, filter: EventFilter | None = None
    ) -> AsyncIterator[list[FTEvent]]:
        """Yield a list of new events filtered by params."""
        response = await self._async_request(
            "GET",
            self.api_features.events_features.updates.href,
            params=filter.params if filter else None,
        )
        while True:
            _LOGGER.debug(response)
            yield [FTEvent(event) for event in response["events"]]
            await asyncio.sleep(1)
            response = await self._async_request(
                "GET",
                response["updates"]["href"],
                params=filter.params if filter else None,
            )
