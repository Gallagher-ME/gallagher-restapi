"""Gallagher item models."""
from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import pytz


class FTITemTypes(Enum):
    """Enumrate FTItem types."""


@dataclass
class FTApiFeatures:
    """FTApiFeatures class."""

    accessGroups: dict[str, Any]
    accessZones: dict[str, Any]
    alarms: dict[str, Any]
    alarmZones: dict[str, Any]
    cardholders: dict[str, Any]
    cardTypes: dict[str, Any]
    competencies: dict[str, Any]
    dayCategories: dict[str, Any]
    doors: dict[str, Any]
    elevators: dict[str, Any]
    events: dict[str, Any]
    fenceZones: dict[str, Any]
    inputs: dict[str, Any]
    interlockGroups: dict[str, Any]
    items: dict[str, Any]
    lockerBanks: dict[str, Any]
    macros: dict[str, Any]
    operatorGroups: dict[str, Any]
    outputs: dict[str, Any]
    personalDataFields: dict[str, Any]
    receptions: dict[str, Any]
    roles: dict[str, Any]
    schedules: dict[str, Any]
    visits: dict[str, Any]

    def href(self, feature: str) -> str:
        """
        Return href link for feature.
        For subfeteatures use format feature/subfeature
        """
        main_feature = sub_feature = ""
        try:
            if "/" in feature:
                main_feature, sub_feature = feature.split("/")
            else:
                main_feature = feature
        except ValueError:
            raise ValueError("Incorrect syntax of feature.")

        if not (attr := getattr(self, main_feature)):
            raise ValueError(f"{main_feature} is not a valid feature")
        if sub_feature and sub_feature not in attr:
            raise ValueError(f"{sub_feature} is not found in {main_feature}")
        return attr[main_feature or sub_feature]["href"]


@dataclass
class FTItemReference:
    """FTItem reference class."""

    href: str = field(default_factory=str)


@dataclass
class FTStatus:
    """FTStatus class."""

    value: str
    type: str


@dataclass
class FTItemType:
    """FTItemType class."""

    id: str
    name: str


@dataclass
class FTItem:
    """FTItem class."""

    id: str
    name: str
    href: str = field(default_factory=str)
    type: dict = field(default_factory=dict)


@dataclass
class FTLinkItem:
    """FTLinkItem class."""

    name: str
    href: str = field(default_factory=str)


@dataclass
class FTAccessGroupMembership:
    """FTAccessGroupMembership base class."""

    status: FTStatus = field(init=False)
    access_group: FTLinkItem = field(init=False)
    active_from: datetime = field(init=False)
    active_until: datetime = field(init=False)
    href: str = field(default_factory=str)

    @property
    def as_dict(self) -> dict[str, Any]:
        """Return json string for post and update."""
        _dict: dict[str, Any] = {"accessgroup": {"href": self.href}}
        if self.active_from:
            _dict["from"] = f"{self.active_from.isoformat()}Z"
        if self.active_until:
            _dict["until"] = f"{self.active_until.isoformat()}Z"
        return _dict

    @classmethod
    def assign_membership(
        cls,
        access_group: FTItem,
        active_from: datetime | None = None,
        active_until: datetime | None = None,
    ) -> FTAccessGroupMembership:
        """Create an FTAccessGroup item to assign."""
        _cls = FTAccessGroupMembership(href=access_group.href)
        if active_from:
            _cls.active_from = active_from
        if active_until:
            _cls.active_until = active_until
        return _cls

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTAccessGroupMembership:
        """Return FTAccessGroupMembership object from dict."""
        _cls = FTAccessGroupMembership()

        if status := kwargs.get("status"):
            _cls.status = FTStatus(**status)
        if access_group := kwargs.get("accessGroup"):
            _cls.access_group = FTLinkItem(**access_group)
        if active_from := kwargs.get("from"):
            _cls.active_from = datetime.fromisoformat(active_from[:-1]).replace(
                tzinfo=pytz.utc
            )
        if active_until := kwargs.get("until"):
            _cls.active_until = datetime.fromisoformat(active_until[:-1]).replace(
                tzinfo=pytz.utc
            )
        return _cls


@dataclass
class FTCardholderCard:
    """FTCardholder card base class."""

    type: FTLinkItem | FTItem
    number: str = field(init=False)
    card_serial_number: str = field(init=False)
    issue_level: int = field(init=False)
    status: FTStatus = field(init=False)
    active_from: datetime = field(init=False)
    active_until: datetime = field(init=False)

    @property
    def as_dict(self) -> dict[str, Any]:
        """Return json string for post and update."""
        _dict: dict[str, Any] = {"type": {"href": self.type.href}}
        if self.number:
            _dict["number"] = self.number
        if self.issue_level:
            _dict["issueLevel"] = self.issue_level
        if self.active_from:
            _dict["from"] = f"{self.active_from.isoformat()}Z"
        if self.active_until:
            _dict["until"] = f"{self.active_until.isoformat()}Z"
        return _dict

    @classmethod
    def create_card(
        cls,
        card_type: FTItem,
        number: str = "",
        issue_level: int | None = None,
        active_from: datetime | None = None,
        active_until: datetime | None = None,
    ) -> FTCardholderCard:
        """Create an FTCardholder card object."""
        _cls = FTCardholderCard(type=card_type)
        if number:
            _cls.number = number
        if issue_level:
            _cls.issue_level = issue_level
        if active_from:
            _cls.active_from = active_from
        if active_until:
            _cls.active_until = active_until
        return _cls

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTCardholderCard:
        """Return FTCardholderCard object from dict."""
        _cls = FTCardholderCard(type=FTLinkItem(**kwargs["type"]))
        if number := kwargs.get("number"):
            _cls.number = number
        if issue_level := kwargs.get("issueLevel"):
            _cls.issue_level = issue_level
        if status := kwargs.get("status"):
            _cls.status = FTStatus(**status)
        if active_from := kwargs.get("from"):
            _cls.active_from = datetime.fromisoformat(active_from[:-1]).replace(
                tzinfo=pytz.utc
            )
        if active_until := kwargs.get("until"):
            _cls.active_until = datetime.fromisoformat(active_until[:-1]).replace(
                tzinfo=pytz.utc
            )
        return _cls


@dataclass
class FTPersonalDataDefinition:
    """FTPersonalDataDefinition class."""

    id: str
    name: str
    type: str
    href: str = field(default_factory=str)


@dataclass
class FTCardholderPdfValue:
    """FTCardholderPdfValue class."""

    name: str
    value: str | FTItemReference = field(init=False)
    notifications: bool = field(init=False)
    definition: FTPersonalDataDefinition = field(init=False)
    href: str = field(init=False)

    @property
    def as_dict(self) -> dict[str, Any]:
        """Return json string for post and update."""
        return {f"@{self.name}": {"notifications": self.notifications}}

    @classmethod
    def create_pdf(
        cls, pdf_definition: FTItem, value: str, enable_notification: bool = False
    ) -> FTCardholderPdfValue:
        """Create FTCardholderPdfValue object for POST."""
        _cls = FTCardholderPdfValue(name=pdf_definition.name)
        _cls.value = value
        _cls.notifications = enable_notification
        return _cls

    @classmethod
    def from_dict(cls, kwargs: dict[str, dict[str, Any]]) -> FTCardholderPdfValue:
        """Return FTCardholderPdfValue object from dict."""
        for name, info in kwargs.items():
            _cls = FTCardholderPdfValue(name=name[1:])
            if value := info.get("value"):
                _cls.value = (
                    FTItemReference(**value) if isinstance(value, dict) else value
                )
            if definition := info.get("definition"):
                _cls.definition = FTPersonalDataDefinition(**definition)
            if href := info.get("href"):
                _cls.href = href
        return _cls


@dataclass
class FTCardholderField:
    """Class to represent FTCardholder field."""

    name: str
    from_dict: Callable[[Any], Any] = lambda val: val
    to_dict: Callable[[Any], Any] = lambda val: val


FTCARDHOLDER_FIELDS: tuple[FTCardholderField, ...] = (
    FTCardholderField(name="href"),
    FTCardholderField(name="id"),
    FTCardholderField(name="name"),
    FTCardholderField(name="firstName"),
    FTCardholderField(name="lastName"),
    FTCardholderField(name="shortName"),
    FTCardholderField(name="description"),
    FTCardholderField(name="authorised"),
    FTCardholderField(
        name="lastSuccessfulAccessTime",
        from_dict=lambda val: datetime.fromisoformat(val[:-1]).replace(tzinfo=pytz.utc),
    ),
    FTCardholderField(
        name="lastSuccessfulAccessZone",
        from_dict=lambda val: FTLinkItem(**val),
    ),
    FTCardholderField(name="serverDisplayName"),
    FTCardholderField(name="division", from_dict=lambda val: FTItemReference(**val)),
    FTCardholderField(name="disableCipherPad"),
    FTCardholderField(name="usercode"),
    FTCardholderField(name="operatorLoginEnabled"),
    FTCardholderField(name="operatorUsername"),
    FTCardholderField(name="operatorPassword"),
    FTCardholderField(name="operatorPasswordExpired"),
    FTCardholderField(name="windowsLoginEnabled"),
    FTCardholderField(name="windowsUsername"),
    FTCardholderField(
        name="personalDataDefinitions",
        from_dict=lambda val: [
            FTCardholderPdfValue.from_dict(pdf_value) for pdf_value in val
        ],
        to_dict=lambda val: [pdf_value.to_dict for pdf_value in val],
    ),
    FTCardholderField(
        name="cards",
        from_dict=lambda val: [FTCardholderCard.from_dict(card) for card in val],
        to_dict=lambda val: [card.to_dict for card in val],
    ),
    FTCardholderField(
        name="accessGroups",
        from_dict=lambda val: [
            FTAccessGroupMembership.from_dict(access_group) for access_group in val
        ],
        to_dict=lambda val: [card.to_dict for card in val],
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
    FTCardholderField(name="edit", from_dict=lambda val: FTItemReference(**val)),
    FTCardholderField(
        name="updateLocation",
        from_dict=lambda val: FTItemReference(**val),
    ),
    FTCardholderField(name="notes"),
    # FTCardholderField(key="notifications", name="notifications", value=lambda val: FTNotification(val)),
    FTCardholderField(name="relationships"),
    FTCardholderField(name="lockers"),
    FTCardholderField(name="elevatorGroups"),
    FTCardholderField(
        name="lastPrintedOrEncodedTime",
        from_dict=lambda val: datetime.fromisoformat(val[:-1]).replace(tzinfo=pytz.utc),
    ),
    FTCardholderField(name="lastPrintedOrEncodedIssueLevel"),
    FTCardholderField(name="redactions"),
)


@dataclass
class FTCardholder:
    """FTCardholder details class."""

    href: str = field(init=False)
    id: str = field(init=False)
    division: FTItemReference | None = None
    name: str = field(init=False)
    firstName: str = field(default="")
    lastName: str = field(default="")
    shortName: str = field(default="")
    description: str = field(default="")
    authorised: bool = field(default=False)
    pdfs: dict[str, Any] = field(default_factory=dict)
    lastSuccessfulAccessTime: datetime = field(init=False)
    lastSuccessfulAccessZone: FTLinkItem = field(init=False)
    serverDisplayName: str = field(init=False)
    disableCipherPad: bool = field(default=False)
    usercode: str = field(default="")
    operatorLoginEnabled: bool = field(default=False)
    operatorUsername: str = field(default="")
    operatorPassword: str = field(default="")
    operatorPasswordExpired: bool = field(default=False)
    windowsLoginEnabled: bool = field(default=False)
    windowsUsername: str = field(default="")
    personalDataDefinitions: dict[str, FTCardholderPdfValue] | None = field(
        default=None
    )
    cards: list[FTCardholderCard] | None = None
    accessGroups: list[FTAccessGroupMembership] | None = None
    # operator_groups: str
    # competencies: str
    # edit: str
    updateLocation: FTItemReference | None = None
    notes: str = field(default="")
    # relationships: Any | None = None
    lockers: Any | None = None
    elevatorGroups: Any | None = None
    lastPrintedOrEncodedTime: datetime | None = None
    lastPrintedOrEncodedIssueLevel: int | None = None
    # redactions: Any | None = None

    @property
    def as_dict(self) -> dict[str, Any]:
        """Return serialized str."""
        _dict: dict[str, Any] = {}
        for cardholder_field in FTCARDHOLDER_FIELDS:
            try:
                if value := getattr(self, cardholder_field.name):
                    _dict[cardholder_field.name] = cardholder_field.to_dict(value)
            except AttributeError:
                continue

        if self.pdfs:
            _dict.update({f"@{name}": value for name, value in self.pdfs.items()})
        return json.loads(json.dumps(_dict, default=lambda o: o.__dict__))

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTCardholder:
        """Return FTCardholder object from dict."""

        _cls = FTCardholder()
        for cardholder_field in FTCARDHOLDER_FIELDS:
            if value := kwargs.get(cardholder_field.name):
                setattr(_cls, cardholder_field.name, cardholder_field.from_dict(value))

        for cardholder_pdf in list(kwargs.keys()):
            if cardholder_pdf.startswith("@"):
                _cls.pdfs[cardholder_pdf[1:]] = kwargs[cardholder_pdf]

        return _cls


# Gallagher alarm and event models
@dataclass
class FTAlarm:
    """FTAlarm summary class"""

    state: str
    href: str = field(default_factory=str)


@dataclass
class FTEventCard:
    """Event card details."""

    number: str
    issue_level: int = field(init=False)
    facility_code: str = field(init=False)

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTEventCard:
        """Return Event card object from dict."""

        _cls = FTEventCard(number=kwargs["number"])
        _cls.issue_level = kwargs["issueLevel"]
        _cls.facility_code = kwargs["facilityCode"]
        return _cls


@dataclass
class FTEventGroup:
    """FTEvent group class."""

    id: str
    name: str
    href: str = field(default_factory=str)
    event_types: list[FTItem] = field(init=False)

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTEventGroup:
        """Return Event card object from dict."""
        event_types = kwargs.pop("eventTypes")
        _cls = FTEventGroup(**kwargs)
        _cls.event_types = [FTItem(**event_type) for event_type in event_types]
        return _cls


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
    EventField(key="id", name="id"),
    EventField(key="server_display_name", name="serverDisplayName"),
    EventField(key="message", name="message"),
    EventField(
        key="time",
        name="time",
        value=lambda val: datetime.fromisoformat(val[:-1]).replace(tzinfo=pytz.utc),
    ),
    EventField(key="occurrences", name="occurrences"),
    EventField(key="priority", name="priority"),
    EventField(key="alarm", name="alarm", value=lambda val: FTAlarm(**val)),
    EventField(key="operator", name="operator", value=lambda val: FTLinkItem(**val)),
    EventField(key="source", name="source", value=lambda val: FTItem(**val)),
    EventField(key="event_group", name="group", value=lambda val: FTItemType(**val)),
    EventField(key="event_type", name="type", value=lambda val: FTItemType(**val)),
    EventField(
        key="event_type2", name="eventType", value=lambda val: FTItemType(**val)
    ),
    EventField(key="division", name="division", value=lambda val: FTItem(**val)),
    EventField(
        key="cardholder",
        name="cardholder",
        value=FTCardholder.from_dict,
    ),
    EventField(
        key="entry_access_zone", name="entryAccessZone", value=lambda val: FTItem(**val)
    ),
    EventField(
        key="exit_access_zone", name="exitAccessZone", value=lambda val: FTItem(**val)
    ),
    EventField(key="door", name="door", value=lambda val: FTLinkItem(**val)),
    EventField(key="access_group", name="accessGroup", value=lambda val: FTItem(**val)),
    EventField(key="card", name="card", value=FTEventCard.from_dict),
    # EventField(
    #     key="modified_item",
    #     name="modifiedItem",
    #     value=lambda val: FTEventCard(val),
    # ),
    EventField(
        key="last_occurrence_time",
        name="lastOccurrenceTime",
        value=lambda val: datetime.fromisoformat(val[:-1]).replace(tzinfo=pytz.utc),
    ),
    EventField(
        key="previous", name="previous", value=lambda val: FTItemReference(**val)
    ),
    EventField(key="next", name="next", value=lambda val: FTItemReference(**val)),
    EventField(key="updates", name="updates", value=lambda val: FTItemReference(**val)),
)


@dataclass(init=False)
class FTEvent:
    """FTEvent summary class."""

    href: str
    id: str
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

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTEvent:
        """Return FTEvent object from dict."""

        _cls = FTEvent()
        for event_field in EVENT_FIELDS:
            if (value := kwargs.get(event_field.name)) or (
                value := kwargs.get(event_field.key)
            ):
                if isinstance(value, dict):
                    value = event_field.value(kwargs[event_field.name])
                setattr(_cls, event_field.key, value)

        return _cls


@dataclass
class EventFilter:
    """Event filter class."""

    top: int | None = None
    after: datetime | None = None
    before: datetime | None = None
    sources: list[FTItem] | list[str] | None = None
    event_types: list[FTItem] | list[str] | None = None
    event_groups: list[FTEventGroup] | list[str] | None = None
    cardholders: list[FTCardholder] | list[str] | None = None
    divisions: list[FTItem] | list[str] | None = None
    related_items: list[FTItem] | list[str] | None = None
    fields: list[str] | None = None
    previous: bool = False

    @property
    def as_dict(self) -> dict[str, Any]:
        """Return event filter as dict."""
        params: dict[str, Any] = {"previous": self.previous}
        if self.top:
            params["top"] = str(self.top)
        if self.after and (after_value := self.after.isoformat()):
            params["after"] = after_value
        if self.before and (before_value := self.before.isoformat()):
            params["after"] = before_value
        if self.sources:
            source_ids = [
                source.id if isinstance(source, FTItem) else source
                for source in self.sources
            ]
            params["source"] = ",".join(source_ids)
        if self.event_types:
            event_type_ids = [
                event_type.id if isinstance(event_type, FTItem) else event_type
                for event_type in self.event_types
            ]
            params["type"] = ",".join(event_type_ids)
        if self.event_groups:
            event_group_ids = [
                event_group.id if isinstance(event_group, FTEventGroup) else event_group
                for event_group in self.event_groups
            ]
            params["group"] = ",".join(event_group_ids)
        if self.cardholders:
            cardholder_ids = [
                cardholder.id if isinstance(cardholder, FTCardholder) else cardholder
                for cardholder in self.cardholders
            ]
            params["cardholder"] = ",".join(cardholder_ids)
        if self.divisions:
            division_ids = [
                division.id if isinstance(division, FTItem) else division
                for division in self.divisions
            ]
            params["division"] = ",".join(division_ids)
        if self.related_items:
            related_item_ids = [
                related_item.id if isinstance(related_item, FTItem) else related_item
                for related_item in self.related_items
            ]
            params["relatedItem"] = ",".join(related_item_ids)
        if self.fields:
            event_fields = [field.name for field in EVENT_FIELDS]
            for event_field in self.fields:
                if (
                    not event_field.startswith("cardholder.pdf_")
                    and event_field not in event_fields
                ):
                    raise ValueError(f"'{event_field}' is not a valid field")
            params["fields"] = ",".join(self.fields)
        return params
