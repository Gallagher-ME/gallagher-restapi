"""Gallagher item models."""
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


class FTItemReference:
    """FTItem reference class."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTItemReference."""

        self.href: str = kwargs.get("href", "")


class FTNavigation(FTItemReference):
    """FTNavigation Class."""


class FTStatus:
    """FTStatus class."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTStatus item."""
        self.value = kwargs["value"]
        self.type = kwargs["type"]


class FTItemType:
    """FTItemType class."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTItem type."""
        self.ftitem_id: str = kwargs["id"]
        self.name: str = kwargs["name"]


class FTItem(FTItemReference):
    """FTItem class."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTItem."""
        super().__init__(kwargs)
        self.ftitem_id: str = kwargs["id"]
        self.name: str = kwargs["name"]


class FTLinkItem(FTItemReference):
    """FTLinkItem class."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTItem link."""
        super().__init__(kwargs)
        self.name: str = kwargs["name"]


class FTApiFeaturesEvents:
    """FTApiFeature events class."""

    def __init__(self, features: dict[str, Any]) -> None:
        """Initialize FTApiFeature events."""
        self.events = FTNavigation(features["events"])
        self.updates = FTNavigation(features["updates"])
        self.event_groups = FTNavigation(features["eventGroups"])
        self.divisions = FTNavigation(features["divisions"])


class FTApiFeaturesAlarms:
    """FTApiFeature alarms class."""

    def __init__(self, features: dict[str, Any]) -> None:
        """Initialize FTApiFeature alarms."""
        self.alarms = FTNavigation(features["alarms"])
        self.updates = FTNavigation(features["updates"])
        self.divisions = FTNavigation(features["divisions"])


class FTApiFeatures:
    """FTApiFeatures class."""

    def __init__(self, features: dict[str, Any]) -> None:
        """Initialize FTApi features."""
        self.items = FTNavigation(features["items"]["items"])
        self.item_types = FTNavigation(features["items"]["itemTypes"])
        self.alarms_features = FTApiFeaturesAlarms(features["alarms"])
        self.events_features = FTApiFeaturesEvents(features["events"])
        self.cardholders = FTNavigation(features["cardholders"]["cardholders"])
        self.personal_data_fields = FTNavigation(
            features["personalDataFields"]["personalDataFields"]
        )


class FTAccessGroupMembership(FTItemReference):
    """FTAccessGroupMembership base class."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTAccessGroupMembership item."""
        super().__init__(kwargs)
        self.status = FTStatus(kwargs["status"])
        self.access_group = FTLinkItem(kwargs["accessGroup"])
        if active_from := kwargs.get("from"):
            self.active_from = datetime.fromisoformat(active_from[:-1]).astimezone(
                timezone.utc
            )
        if active_until := kwargs.get("until"):
            self.active_until = datetime.fromisoformat(active_until[:-1]).astimezone(
                timezone.utc
            )


class FTCardholderCard(FTItemReference):
    """FTCardholder card base class."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTCardholder card item."""
        super().__init__(kwargs)
        self.number: str = kwargs["number"]
        self.card_serial_number: str | None = kwargs.get("cardSerialNumber")
        self.issue_level: int | None = kwargs.get("issueLevel")
        self.status = FTStatus(kwargs["status"])
        self.type = FTLinkItem(kwargs["type"])
        if access_group := kwargs.get("accessGroups"):
            self.access_group = FTLinkItem(access_group)
        if active_from := kwargs.get("from"):
            self.active_from = datetime.fromisoformat(active_from[:-1]).astimezone(
                timezone.utc
            )
        if active_until := kwargs.get("until"):
            self.active_until = datetime.fromisoformat(active_until[:-1]).astimezone(
                timezone.utc
            )


class FTPersonalDataDefinition(FTItem):
    """FTPersonalDataDefinition class."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTPersonalDataDefinition item."""
        super().__init__(kwargs)
        self.type = kwargs["type"]


class FTCardholderPdfValue(FTItemReference):
    """FTCardholderPdfValue class."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTCardholderPdfValue item."""
        super().__init__(kwargs)
        self.definition = FTPersonalDataDefinition(kwargs["definition"])
        if value := kwargs.get("value"):
            if isinstance(value, dict):
                self.value = FTNavigation(value)
            else:
                self.value = value


@dataclass
class FTCardholderField:
    """Class to represent FTCardholder field."""

    key: str
    name: str
    value: Callable[[Any], Any] = lambda val: val


FTCARDHOLDER_FIELDS: tuple[FTCardholderField, ...] = (
    FTCardholderField(key="href", name="href"),
    FTCardholderField(key="ftitem_id", name="id"),
    FTCardholderField(key="name", name="name"),
    FTCardholderField(key="first_name", name="firstName"),
    FTCardholderField(key="last_name", name="lastName"),
    FTCardholderField(key="short_name", name="shortName"),
    FTCardholderField(key="description", name="description"),
    FTCardholderField(key="authorised", name="authorised"),
    FTCardholderField(
        key="last_successful_access_time",
        name="lastSuccessfulAccessTime",
        value=lambda val: datetime.fromisoformat(val[:-1]).astimezone(timezone.utc),
    ),
    FTCardholderField(
        key="last_successful_access_zone",
        name="lastSuccessfulAccessZone",
        value=lambda val: FTLinkItem(val),
    ),
    FTCardholderField(key="server_display_name", name="serverDisplayName"),
    FTCardholderField(
        key="division", name="division", value=lambda val: FTItemReference(val)
    ),
    FTCardholderField(key="disable_cipher_pad", name="disableCipherPad"),
    FTCardholderField(key="user_code", name="usercode"),
    FTCardholderField(key="operator_login_enabled", name="operatorLoginEnabled"),
    FTCardholderField(key="operator_username", name="operatorUsername"),
    FTCardholderField(key="operator_password", name="operatorPassword"),
    FTCardholderField(key="operator_password_expired", name="operatorPasswordExpired"),
    FTCardholderField(key="windows_login_enabled", name="windowsLoginEnabled"),
    FTCardholderField(key="windows_username", name="windowsUsername"),
    FTCardholderField(
        key="personal_data_definitions",
        name="personalDataDefinitions",
        value=lambda val: {
            pdf_name[1:]: FTCardholderPdfValue(pdf_value)
            for pdf in val
            for pdf_name, pdf_value in pdf.items()
        },
    ),
    FTCardholderField(
        key="cards",
        name="cards",
        value=lambda val: [FTCardholderCard(card) for card in val],
    ),
    FTCardholderField(
        key="access_groups",
        name="accessGroups",
        value=lambda val: [
            FTAccessGroupMembership(access_group) for access_group in val
        ],
    ),
    # FTCardholderField(
    #     key="operator_groups",
    #     name="operatorGroups",
    #     value=lambda val: [
    #         FTOperatorGroup(operator_group) for operator_group in val
    #     ],
    # ),
    # FTCardholderField(
    #     key="competencies",
    #     name="competencies",
    #     value=lambda val: [
    #         FTCompetency(competency) for competency in val
    #     ],
    # ),
    FTCardholderField(key="edit", name="edit", value=lambda val: FTItemReference(val)),
    FTCardholderField(
        key="update_location",
        name="updateLocation",
        value=lambda val: FTItemReference(val),
    ),
    FTCardholderField(key="notes", name="notes"),
    # FTCardholderField(key="notifications", name="notifications", value=lambda val: FTNotification(val)),
    FTCardholderField(key="relationships", name="relationships"),
    FTCardholderField(key="lockers", name="lockers"),
    FTCardholderField(key="elevatorGroups", name="elevatorGroups"),
    FTCardholderField(
        key="last_printed_or_encodedTime",
        name="lastPrintedOrEncodedTime",
        value=lambda val: datetime.fromisoformat(val[:-1]).astimezone(timezone.utc),
    ),
    FTCardholderField(
        key="last_printed_or_encoded_issue_level", name="lastPrintedOrEncodedIssueLevel"
    ),
    FTCardholderField(key="redactions", name="redactions"),
)


class FTCardholder:
    """FTCardholder details class."""

    href: str
    ftitem_id: str
    name: str
    first_name: str
    last_name: str
    short_name: str
    description: str
    authorised: bool
    last_successful_access_time: datetime
    last_successful_access_zone: FTLinkItem
    server_display_name: str
    division: FTItemReference
    disable_cipher_pad: bool
    user_code: str
    operator_login_enabled: bool
    operator_username: str
    operator_password: str
    operator_password_expired: bool
    windows_login_enabled: bool
    windows_username: str
    personal_data_definitions: dict[str, FTCardholderPdfValue]
    cards: list[FTCardholderCard]
    access_groups: list[FTAccessGroupMembership]
    # operator_groups: str
    # competencies: str
    # edit: str
    update_location: FTItemReference
    notes: str
    relationships: Any
    lockers: Any
    elevatorGroups: Any
    last_printed_or_encodedTime: datetime
    last_printed_or_encoded_issue_level: int
    redactions: Any

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize FTCardholder item."""
        self.pdfs: dict[str, Any] = {
            pdf_name[1:]: pdf_value
            for pdf_name, pdf_value in kwargs.items()
            if pdf_name.startswith("@")
        }
        for cardholder_field in FTCARDHOLDER_FIELDS:
            if cardholder_field.name in kwargs:
                setattr(
                    self,
                    cardholder_field.key,
                    cardholder_field.value(kwargs[cardholder_field.name]),
                )


# Gallagher alarm and event models
class FTAlarm(FTItemReference):
    """FTAlarm summary class"""

    def __init__(self, kwargs: dict[str, Any]):
        """Initialize FTAlarm."""
        super().__init__(kwargs)
        self.state: str = kwargs["state"]


class FTEventCard:
    """Event card details."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        """Initialize event card."""
        self.number: str = kwargs["number"]
        self.issue_level: int = kwargs["issueLevel"]
        self.facility_code: str = kwargs["facilityCode"]


class FTEventType(FTItem):
    """FTEvent type class."""


class FTEventGroup(FTItem):
    """FTEvent group class."""

    def __init__(self, kwargs: dict[str, Any]):
        """Initialize FTEvent group."""
        super().__init__(kwargs)
        self.event_types: list[FTEventType] = [
            FTEventType(event_type) for event_type in kwargs["eventTypes"]
        ]


@dataclass
class EventField:
    """Class to represent Event field."""

    key: str
    name: str
    value: Callable[[Any], Any] = lambda val: val


EVENT_FIELDS: tuple[EventField, ...] = (
    EventField(key="defaults", name="defaults"),
    EventField(key="details", name="details"),
    EventField(key="href", name="href"),
    EventField(key="ftitem_id", name="id"),
    EventField(key="server_display_name", name="serverDisplayName"),
    EventField(key="message", name="message"),
    EventField(
        key="time",
        name="time",
        value=lambda val: datetime.fromisoformat(val[:-1]).astimezone(timezone.utc),
    ),
    EventField(key="occurrences", name="occurrences"),
    EventField(key="priority", name="priority"),
    EventField(key="alarm", name="alarm", value=lambda val: FTAlarm(val)),
    EventField(key="operator", name="operator", value=lambda val: FTLinkItem(val)),
    EventField(key="source", name="source", value=lambda val: FTItem(val)),
    EventField(key="event_group", name="group", value=lambda val: FTItemType(val)),
    EventField(key="event_type", name="type", value=lambda val: FTItemType(val)),
    EventField(key="event_type2", name="eventType", value=lambda val: FTItemType(val)),
    EventField(key="division", name="division", value=lambda val: FTItem(val)),
    EventField(
        key="cardholder", name="cardholder", value=lambda val: FTCardholder(val)
    ),
    EventField(
        key="entry_access_zone", name="entryAccessZone", value=lambda val: FTItem(val)
    ),
    EventField(
        key="exit_access_zone", name="exitAccessZone", value=lambda val: FTItem(val)
    ),
    EventField(key="door", name="door", value=lambda val: FTLinkItem(val)),
    EventField(
        key="access_group", name="accessGroup", value=lambda val: FTItemReference(val)
    ),
    EventField(key="card", name="card", value=lambda val: FTEventCard(val)),
    # EventField(
    #     key="modified_item",
    #     name="modifiedItem",
    #     value=lambda val: FTEventCard(val),
    # ),
    EventField(
        key="last_occurrence_time",
        name="lastOccurrenceTime",
        value=lambda val: datetime.fromisoformat(val[:-1]).astimezone(timezone.utc),
    ),
    EventField(key="previous", name="previous", value=lambda val: FTItemReference(val)),
    EventField(key="next", name="next", value=lambda val: FTItemReference(val)),
    EventField(key="updates", name="updates", value=lambda val: FTItemReference(val)),
)


class FTEvent:
    """FTEvent summary class."""

    href: str
    ftitem_id: str
    details: str
    server_display_name: str
    message: str
    time: datetime
    occurrences: int
    priority: int
    alarm: FTAlarm
    operator: FTLinkItem
    source: FTItem
    event_group: FTItemType
    event_type: FTItemType
    event_type2: FTItemType
    division: FTItem
    cardholder: FTCardholder
    entry_access_zone: FTItem
    exit_access_zone: FTItem
    door: FTLinkItem
    access_group: FTItemReference
    card: FTEventCard
    # modified_item: str
    last_occurrence_time: datetime
    previous: FTItemReference
    next: FTItemReference
    updates: FTItemReference

    def __init__(self, kwargs: dict[str, Any]):
        """Initialize FTEvent."""
        for event_field in EVENT_FIELDS:
            if event_field.name in kwargs:
                setattr(
                    self,
                    event_field.key,
                    event_field.value(kwargs[event_field.name]),
                )


class EventFilter:
    """Event filter class."""

    def __init__(
        self,
        top: int | None = None,
        after: datetime | None = None,
        before: datetime | None = None,
        sources: list[FTItem] | list[str] | None = None,
        event_types: list[FTEventType] | list[str] | None = None,
        event_groups: list[FTEventGroup] | list[str] | None = None,
        cardholders: list[FTCardholder] | list[str] | None = None,
        divisions: list[FTItem] | list[str] | None = None,
        related_items: list[FTItem] | list[str] | None = None,
        fields: list[str] | None = None,
        previous: bool = False,
    ) -> None:
        """Initialize event filter."""
        self.params: dict[str, Any] = {"previous": previous}
        if top:
            self.params["top"] = str(top)
        if after and (after_value := after.isoformat()):
            self.params["after"] = after_value
        if before and (before_value := before.isoformat()):
            self.params["after"] = before_value
        if sources:
            source_ids = [
                source.ftitem_id if isinstance(source, FTItem) else source
                for source in sources
            ]
            self.params["source"] = ",".join(source_ids)
        if event_types:
            event_type_ids = [
                event_type.ftitem_id
                if isinstance(event_type, FTEventType)
                else event_type
                for event_type in event_types
            ]
            self.params["type"] = ",".join(event_type_ids)
        if event_groups:
            event_group_ids = [
                event_group.ftitem_id
                if isinstance(event_group, FTEventGroup)
                else event_group
                for event_group in event_groups
            ]
            self.params["group"] = ",".join(event_group_ids)
        if cardholders:
            cardholder_ids = [
                cardholder.ftitem_id
                if isinstance(cardholder, FTCardholder)
                else cardholder
                for cardholder in cardholders
            ]
            self.params["cardholder"] = ",".join(cardholder_ids)
        if divisions:
            division_ids = [
                division.ftitem_id if isinstance(division, FTItem) else division
                for division in divisions
            ]
            self.params["division"] = ",".join(division_ids)
        if related_items:
            related_item_ids = [
                related_item.ftitem_id
                if isinstance(related_item, FTItem)
                else related_item
                for related_item in related_items
            ]
            self.params["relatedItem"] = ",".join(related_item_ids)
        if fields:
            event_fields = [field.name for field in EVENT_FIELDS]
            for field in fields:
                if (
                    not field.startswith("cardholder.pdf_")
                    and field not in event_fields
                ):
                    raise ValueError(f"'{field}' is not a valid field")
            self.params["fields"] = ",".join(fields)