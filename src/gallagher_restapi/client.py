"""Gallagher REST api python library."""

import asyncio
import base64
import logging
from datetime import datetime
from enum import StrEnum
from json import JSONDecodeError
from ssl import SSLError
from typing import Any, AsyncIterator, cast

import httpx

from .exceptions import ConnectError, GllApiError, RequestError, UnauthorizedError
from .models import (
    CardholderChange,
    EventFilter,
    EventPost,
    FTAccessGroup,
    FTAccessZone,
    FTAlarm,
    FTAlarmZone,
    FTApiFeatures,
    FTCardholder,
    FTCardType,
    FTDoor,
    FTEvent,
    FTEventGroup,
    FTFenceZone,
    FTInput,
    FTItem,
    FTItemReference,
    FTItemStatus,
    FTLinkItem,
    FTLocker,
    FTLockerBank,
    FTNewCardholder,
    FTOperatorGroup,
    FTOperatorGroupMembership,
    FTOutput,
    FTPersonalDataFieldDefinition,
    HTTPMethods,
    SortMethod,
)

_LOGGER = logging.getLogger(__name__)


class CloudGateway(StrEnum):
    """Cloud Gateways."""

    AU_GATEWAY = "commandcentre-api-au.security.gallagher.cloud"
    US_GATEWAY = "commandcentre-api-us.security.gallagher.cloud"


class Client:
    """Gallagher REST api base client."""

    def __init__(
        self,
        api_key: str,
        *,
        host: str = "localhost",
        port: int = 8904,
        cloud_gateway: CloudGateway | None = None,
        token: str | None = None,
        httpx_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize REST api client."""
        if cloud_gateway is not None:
            host = cloud_gateway.value
            port = 443
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
        self.api_features: FTApiFeatures = None  # type: ignore[assignment]
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
        params: dict[str, Any] | None = None,
        extra_fields: list[str] | None = None,
        name: str | None = None,
        description: str | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> dict[str, Any]:
        """Send a http request and return the response."""
        params = params or {}
        if extra_fields:
            if "defaults" not in extra_fields:
                extra_fields.append("defaults")
            params["fields"] = ",".join(extra_fields)
        params.update(
            {
                key: value
                for key, value in {
                    "division": ",".join(division) if division else None,
                    "name": name,
                    "description": description,
                    "sort": sort,
                    "top": top,
                }.items()
                if value is not None
            }
        )

        _LOGGER.debug(
            "Sending %s request to endpoint: %s, data: %s, params: %s",
            method,
            endpoint,
            data,
            params,
        )
        try:
            response = await self.httpx_client.request(
                method, endpoint, params=params or None, json=data
            )
        except (httpx.RequestError, SSLError) as err:
            raise ConnectError(
                f"Connection failed while sending request: {err}"
            ) from err
        _LOGGER.debug(
            "status_code: %s, response: %s", response.status_code, response.text
        )
        if httpx.codes.is_error(response.status_code):
            if response.status_code == httpx.codes.UNAUTHORIZED:
                raise UnauthorizedError(
                    "Unauthorized request. Ensure api key is correct"
                )
            if response.status_code == httpx.codes.NOT_FOUND:
                message = (
                    "Requested item does not exist or "
                    "your operator does not have the privilege to view it"
                )
            elif response.status_code == httpx.codes.SERVICE_UNAVAILABLE:
                message = "Service Unavailable"
            else:
                try:
                    message = cast(dict[str, Any], response.json()).get(
                        "message", "Invalid operation"
                    )
                except JSONDecodeError:
                    message = "Unknown error"
            raise RequestError(message)
        if response.status_code == httpx.codes.CREATED:
            return {"location": response.headers.get("location")}
        if response.status_code == httpx.codes.NO_CONTENT:
            return {}
        if "application/json" in response.headers.get("content-type"):
            return response.json()
        return {"results": response.content}

    async def initialize(self) -> None:
        """Connect to Server and initialize data."""
        response = await self._async_request(HTTPMethods.GET, f"{self.server_url}/api/")
        self.api_features = FTApiFeatures.from_dict(response["features"])
        self.version = response["version"]
        await self._update_item_types()
        await self._update_event_types()

    async def _update_item_types(self) -> None:
        """Get FTItem types."""
        response = await self._async_request(
            HTTPMethods.GET, self.api_features.href("items/itemTypes")
        )
        if response.get("itemTypes"):
            self._item_types = {
                item_type["name"]: item_type["id"]
                for item_type in response["itemTypes"]
                if item_type["name"]
            }

    async def get_item(
        self,
        *,
        id: str | None = None,
        item_types: list[str] | None = None,
        name: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTItem]:
        """Get FTItems filtered by type and name."""
        items: list[FTItem] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('items')}/{id}",
                extra_fields=extra_fields,
            ):
                items = [FTItem.from_dict(response)]

        else:
            type_ids: list[str] = []
            for item_type in item_types or []:
                if (type_id := self._item_types.get(item_type)) is None:
                    raise ValueError(f"Unknown item type: {item_type}")
                type_ids.append(type_id)
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("items"),
                params={"type": ",".join(type_ids)},
                extra_fields=extra_fields,
                name=name,
                division=division,
                sort=sort,
                top=top,
            )
            items = [FTItem.from_dict(item) for item in response["results"]]
        return items

    # region Access zone methods
    async def get_access_zone(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTAccessZone]:
        """Get Access zones filtered by name."""
        access_zones: list[FTAccessZone] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('accessZones')}/{id}",
                extra_fields=extra_fields,
            ):
                access_zones = [FTAccessZone.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("accessZones"),
                extra_fields=extra_fields,
                name=name,
                description=description,
                division=division,
                sort=sort,
                top=top,
            )
            access_zones = [
                FTAccessZone.from_dict(item) for item in response["results"]
            ]
        return access_zones

    async def override_access_zone(
        self,
        command: FTItemReference,
        *,
        end_time: datetime | None = None,
        zone_count: int | None = None,
    ) -> None:
        """POST an override to an access zone."""
        data: dict[str, Any] = {}
        if end_time:
            data["endTime"] = f"{end_time.isoformat()}Z"
        if zone_count:
            data["zoneCount"] = zone_count
        await self._async_request(
            HTTPMethods.POST,
            command.href,
            data=data if data else None,
        )

    # endregion Access zone methods

    # region Alarm zone methods
    async def get_alarm_zone(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTAlarmZone]:
        """Return list of Alarm zone items."""
        alarm_zones: list[FTAlarmZone] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('alarmZones')}/{id}",
                extra_fields=extra_fields,
            ):
                alarm_zones = [FTAlarmZone.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("alarmZones"),
                extra_fields=extra_fields,
                name=name,
                description=description,
                division=division,
                sort=sort,
                top=top,
            )
            alarm_zones = [FTAlarmZone.from_dict(item) for item in response["results"]]
        return alarm_zones

    async def override_alarm_zone(
        self,
        command: FTItemReference,
        *,
        end_time: datetime | None = None,
    ) -> None:
        """POST an override to an alarm zone."""
        data: dict[str, Any] = {}
        if end_time:
            data["endTime"] = f"{end_time.isoformat()}Z"
        await self._async_request(
            HTTPMethods.POST,
            command.href,
            data=data if data else None,
        )

    # endregion Alarm zone methods

    # region Fence zone methods
    async def get_fence_zone(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTFenceZone]:
        """Get Fence zones with filteration."""
        fence_zones: list[FTFenceZone] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('fenceZones')}/{id}",
                extra_fields=extra_fields,
            ):
                fence_zones = [FTFenceZone.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("fenceZones"),
                extra_fields=extra_fields,
                name=name,
                description=description,
                division=division,
                sort=sort,
                top=top,
            )
            fence_zones = [FTFenceZone.from_dict(item) for item in response["results"]]
        return fence_zones

    async def override_fence_zone(
        self,
        command: FTItemReference,
    ) -> None:
        """POST an override to a fence zone."""
        await self._async_request(HTTPMethods.POST, command.href)

    # endregion Fence zone methods

    # region Input methods
    async def get_input(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTInput]:
        """Return list of Alarm zone items."""
        inputs: list[FTInput] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('inputs')}/{id}",
                extra_fields=extra_fields,
            ):
                inputs = [FTInput.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("inputs"),
                extra_fields=extra_fields,
                name=name,
                description=description,
                division=division,
                sort=sort,
                top=top,
            )
            inputs = [FTInput.from_dict(item) for item in response["results"]]
        return inputs

    async def override_input(
        self,
        command: FTItemReference,
    ) -> None:
        """POST an override to an input."""
        await self._async_request(HTTPMethods.POST, command.href)

    # endregion Input methods

    # region Output methods
    async def get_output(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTOutput]:
        """Return list of output items."""
        outputs: list[FTOutput] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('outputs')}/{id}",
                extra_fields=extra_fields,
            ):
                outputs = [FTOutput.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("outputs"),
                extra_fields=extra_fields,
                name=name,
                description=description,
                division=division,
                sort=sort,
                top=top,
            )
            outputs = [FTOutput.from_dict(item) for item in response["results"]]
        return outputs

    async def override_output(
        self,
        command: FTItemReference,
        *,
        end_time: datetime | None = None,
    ) -> None:
        """POST an override to an output."""
        data: dict[str, Any] = {}
        if end_time:
            data["endTime"] = f"{end_time.isoformat()}Z"
        await self._async_request(
            HTTPMethods.POST,
            command.href,
            data=data if data else None,
        )

    # endregion Output methods

    # region Door methods
    async def get_door(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTDoor]:
        """Return list of doors."""
        doors: list[FTDoor] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('doors')}/{id}",
                extra_fields=extra_fields,
            ):
                doors = [FTDoor.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("doors"),
                extra_fields=extra_fields,
                name=name,
                description=description,
                division=division,
                sort=sort,
                top=top,
            )
            doors = [FTDoor.from_dict(door) for door in response["results"]]
        return doors

    async def override_door(self, command: FTItemReference) -> None:
        """override door."""
        await self._async_request(HTTPMethods.POST, command.href)

    # endregion Door methods

    # region Cardholder methods
    async def get_card_type(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTCardType]:
        """Return list of card type items."""
        card_types: list[FTCardType] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('cardTypes')}/{id}",
                extra_fields=extra_fields,
            ):
                card_types = [FTCardType.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("cardTypes/assign"),
                extra_fields=extra_fields,
                name=name,
                description=description,
                division=division,
                sort=sort,
                top=top,
            )
            card_types = [FTCardType.from_dict(item) for item in response["results"]]
        return card_types

    async def get_access_group(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTAccessGroup]:
        """Get Access groups filtered by name."""
        access_groups: list[FTAccessGroup] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('accessGroups')}/{id}",
                extra_fields=extra_fields,
            ):
                access_groups = [FTAccessGroup.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("accessGroups"),
                extra_fields=extra_fields,
                name=name,
                description=description,
                division=division,
                sort=sort,
                top=top,
            )
            access_groups = [
                FTAccessGroup.from_dict(item) for item in response["results"]
            ]
        return access_groups

    async def get_operator_group(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTOperatorGroup]:
        """Get Operator groups."""
        response = await self._async_request(
            HTTPMethods.GET,
            self.api_features.href("operatorGroups"),
            extra_fields=extra_fields or ["cardholders"],
            name=name,
            description=description,
            division=division,
            sort=sort,
            top=top,
        )
        return [FTOperatorGroup.from_dict(item) for item in response["results"]]

    async def get_operator_group_members(
        self, *, href: str, extra_fields: list[str] | None = None
    ) -> list[FTLinkItem]:
        """Get Operator group members."""
        response = await self._async_request(
            HTTPMethods.GET, href, extra_fields=extra_fields
        )
        operator_group_memberships = [
            FTOperatorGroupMembership.from_dict(item)
            for item in response["cardholders"]
        ]
        return [item.cardholder for item in operator_group_memberships]

    async def get_personal_data_field(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTPersonalDataFieldDefinition]:
        """Return List of available personal data fields."""
        pdfs: list[FTPersonalDataFieldDefinition] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('personalDataFields')}/{id}",
                extra_fields=extra_fields,
            ):
                pdfs = [FTPersonalDataFieldDefinition.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("personalDataFields"),
                name=name,
                extra_fields=extra_fields,
                division=division,
                sort=sort,
                top=top,
            )
            pdfs = [
                FTPersonalDataFieldDefinition.from_dict(pdf)
                for pdf in response["results"]
            ]

        return pdfs

    async def get_image_from_pdf(self, pdf_reference: FTItemReference) -> str | None:
        """Returns base64 string of the image field."""
        if response := await self._async_request(HTTPMethods.GET, pdf_reference.href):
            if not isinstance(response.get("results"), bytes):
                raise ValueError(f"{pdf_reference.href} is not an image href")
            return base64.b64encode(response["results"]).decode("utf-8")
        return None

    async def _search_cardholders(
        self,
        *,
        name: str | None = None,
        pdfs: dict[str, str] | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> dict[str, Any]:
        """Fetch cardholders from the server."""
        params: dict[str, str] = {}
        if pdfs:
            for pdf, value in pdfs.items():
                if not pdf.isdigit():
                    if not (pdf_field := await self.get_personal_data_field(name=pdf)):
                        raise GllApiError(f"pdf field: {pdf} not found")
                    # if pdf name is correct the result should include one item only
                    pdf = pdf_field[0].id
                params.update({f"pdf_{pdf}": value})

        return await self._async_request(
            HTTPMethods.GET,
            self.api_features.href("cardholders"),
            params=params,
            name=name,
            extra_fields=extra_fields,
            division=division,
            sort=sort,
            top=top,
        )

    async def get_cardholder(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        pdfs: dict[str, str] | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTCardholder]:
        """Return list of cardholders."""
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('cardholders')}/{id}",
                extra_fields=extra_fields,
            ):
                return [FTCardholder.from_dict(response)]

        response = await self._search_cardholders(
            name=name,
            pdfs=pdfs,
            extra_fields=extra_fields,
            division=division,
            sort=sort,
            top=top,
        )
        _LOGGER.debug(response)
        return [
            FTCardholder.from_dict(cardholder) for cardholder in response["results"]
        ]

    async def yield_cardholders(
        self,
        *,
        name: str | None = None,
        pdfs: dict[str, str] | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> AsyncIterator[list[FTCardholder]]:
        """Return Async iterator list of cardholders."""
        response = await self._search_cardholders(
            name=name,
            pdfs=pdfs,
            extra_fields=extra_fields,
            division=division,
            sort=sort,
            top=top or 100,
        )
        while True:
            _LOGGER.debug(response)
            yield [
                FTCardholder.from_dict(cardholder) for cardholder in response["results"]
            ]
            await asyncio.sleep(1)
            if not (next_link := response.get("next")):
                break
            response = await self._async_request(HTTPMethods.GET, next_link["href"])

    async def get_cardholder_changes(self, href) -> tuple[list[CardholderChange], str]:
        """Return list of cardholder changes."""
        response = await self._async_request(HTTPMethods.GET, href)
        changes = [CardholderChange.from_dict(change) for change in response["results"]]
        return changes, response["next"]["href"]

    async def get_cardholder_changes_href(
        self,
        *,
        top: int | None = None,
        filter: list[str] | None = None,
        cardholder_fields: list[str] | None = None,
        extra_fields: list[str] | None = None,
    ) -> str:
        """Return the next href to get cardholder changes."""
        params: dict[str, Any] = {}
        if top:
            params["top"] = top
        if filter:
            params["filter"] = ",".join(filter)
        if cardholder_fields:
            params["fields"] = ",".join(
                f"cardholder.{field}" for field in cardholder_fields
            )
        if extra_fields:
            fields = params.setdefault("fields", "")
            params["fields"] = f"{fields},{','.join(extra_fields)}"

        response = await self._async_request(
            HTTPMethods.GET,
            self.api_features.href("cardholders/changes"),
            params=params or None,
        )
        return response["next"]["href"]

    async def add_cardholder(self, cardholder: FTNewCardholder) -> FTItemReference:
        """Add a new cardholder in Gallagher."""
        response = await self._async_request(
            HTTPMethods.POST,
            self.api_features.href("cardholders"),
            data=cardholder.as_dict(),
        )
        return FTItemReference(response["location"])

    async def update_cardholder(
        self, cardholder_href: str, cardholder_updates: FTNewCardholder
    ) -> None:
        """Update existing cardholder in Gallagher."""
        await self._async_request(
            HTTPMethods.PATCH,
            cardholder_href,
            data=cardholder_updates.as_dict(),
        )

    async def remove_cardholder(self, cardholder_href: str) -> None:
        """Remove existing cardholder in Gallagher."""
        await self._async_request(HTTPMethods.DELETE, cardholder_href)

    # endregion Cardholder methods

    # region Event methods
    async def _update_event_types(self) -> None:
        """Fetch list of event groups and types from server."""
        response = await self._async_request(
            HTTPMethods.GET, self.api_features.href("events/eventGroups")
        )

        for item in response["eventGroups"]:
            event_group = FTEventGroup.from_dict(item)
            self.event_groups[event_group.name] = event_group

        for event_group in self.event_groups.values():
            self.event_types.update(
                {event_type.name: event_type for event_type in event_group.eventTypes}
            )

    async def get_events(
        self, event_filter: EventFilter | None = None
    ) -> list[FTEvent]:
        """Return list of events filtered by params."""
        events: list[FTEvent] = []
        if response := await self._async_request(
            HTTPMethods.GET,
            self.api_features.href("events"),
            params=event_filter.as_dict() if event_filter else None,
        ):
            events = [FTEvent.from_dict(event) for event in response["events"]]
        return events

    async def get_new_events(
        self,
        event_filter: EventFilter | None = None,
        next: str | None = None,
    ) -> tuple[list[FTEvent], str]:
        """
        Return new events filtered by params and the link for the next event search.
        """
        if next is not None:
            response = await self._async_request(
                HTTPMethods.GET,
                next,
            )
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("events"),
                params=event_filter.as_dict() if event_filter else None,
            )
        _LOGGER.debug(response)
        events: list[FTEvent] = [
            FTEvent.from_dict(event) for event in response["events"]
        ]
        next_href: str = response["next"]["href"]
        return (events, next_href)

    async def yield_new_events(
        self, event_filter: EventFilter | None = None
    ) -> AsyncIterator[list[FTEvent]]:
        """Yield a list of new events filtered by params."""
        response = await self._async_request(
            HTTPMethods.GET,
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
                HTTPMethods.GET,
                response["updates"]["href"],
                params=event_filter.as_dict() if event_filter else None,
            )

    async def push_event(self, event: EventPost) -> FTItemReference | None:
        """Push a new event to Gallagher and return the event href."""
        response = await self._async_request(
            HTTPMethods.POST, self.api_features.href("events"), data=event.as_dict()
        )
        if "location" in response:
            return FTItemReference(response["location"])
        return None

    # endregion Event methods

    # region Alarm methods

    async def get_alarms(self, extra_fields: list[str] | None = None) -> list[FTAlarm]:
        """Return list of alarms."""
        alarms: list[FTAlarm] = []
        if response := await self._async_request(
            HTTPMethods.GET, self.api_features.href("alarms"), extra_fields=extra_fields
        ):
            alarms = [FTAlarm.from_dict(alarm) for alarm in response["alarms"]]
        return alarms

    async def yield_new_alarms(
        self, extra_fields: list[str] | None = None
    ) -> AsyncIterator[list[FTAlarm]]:
        """Yield a list of new alarms."""
        response = await self._async_request(
            HTTPMethods.GET,
            self.api_features.href("alarms/updates"),
            extra_fields=extra_fields,
        )
        while True:
            _LOGGER.debug(response)
            yield [FTAlarm.from_dict(alarm) for alarm in response["updates"]]
            await asyncio.sleep(1)
            response = await self._async_request(
                HTTPMethods.GET, response["next"]["href"], extra_fields=extra_fields
            )

    async def alarm_action(self, action: FTItemReference, comment: str | None) -> None:
        """post an alarm action (with optional comment)."""
        await self._async_request(
            HTTPMethods.POST,
            action.href,
            data={"comment": comment} if comment else None,
        )

    # endregion Alarm methods

    # region Status and override methods
    async def get_item_status(
        self,
        item_ids: list[str] | None = None,
        next_link: FTItemReference | None = None,
    ) -> tuple[list[FTItemStatus], FTItemReference]:
        """Subscribe to items status and return list of updates with next link."""
        if next_link:
            response = await self._async_request(HTTPMethods.GET, next_link.href)
        elif item_ids:
            response = await self._async_request(
                HTTPMethods.POST,
                self.api_features.href("items/updates"),
                data={"itemIds": item_ids},
            )
        else:
            raise ValueError("item ids or a next link must be provided")
        return (
            [FTItemStatus(**item) for item in response["updates"]],
            FTItemReference(**response["next"]),
        )

    # endregion Status and override methods

    # region Lockers methods
    async def get_locker_bank(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        extra_fields: list[str] | None = None,
        division: list[str] | None = None,
        sort: SortMethod | None = None,
        top: int | None = None,
    ) -> list[FTLockerBank]:
        """Return list of locker banks."""
        locker_banks: list[FTLockerBank] = []
        if id:
            if response := await self._async_request(
                HTTPMethods.GET,
                f"{self.api_features.href('lockerBanks')}/{id}",
                extra_fields=extra_fields,
            ):
                locker_banks = [FTLockerBank.from_dict(response)]
        else:
            response = await self._async_request(
                HTTPMethods.GET,
                self.api_features.href("lockerBanks"),
                extra_fields=extra_fields,
                name=name,
                description=description,
                division=division,
                sort=sort,
                top=top,
            )
            locker_banks = [
                FTLockerBank.from_dict(locker) for locker in response["results"]
            ]
        return locker_banks

    async def get_locker(self, id: str | None = None) -> FTLocker | None:
        """Return locker object."""
        response: dict[str, Any] = await self._async_request(
            HTTPMethods.GET, f"{self.server_url}/api/lockers/{id}"
        )
        return FTLocker.from_dict(response) if response else None

    async def override_locker(self, command: FTItemReference) -> None:
        """override locker."""
        await self._async_request(HTTPMethods.POST, command.href)

    # endregion Lockers methods
