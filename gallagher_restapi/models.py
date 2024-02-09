"""Gallagher item models."""
from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

import pytz
from dacite import from_dict


class HTTPMethods(StrEnum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"


class PatchAction(StrEnum):
    """Enumerate patch actions."""

    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"


class SortMethod(StrEnum):
    """Enumerate door sorting."""

    ID_ASC = "id"
    ID_DSC = "-id"
    NAME_ASC = "name"
    NAME_DSC = "-name"


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
    divisions: dict[str, Any]
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
        For sub_features use format main_feature/sub_feature
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
        return attr[sub_feature or main_feature]["href"]


@dataclass
class FTItemReference:
    """FTItem reference class."""

    href: str


@dataclass
class FTStatus:
    """FTStatus class."""

    value: str
    type: str = ""


@dataclass
class FTItemType:
    """FTItemType class."""

    id: str
    name: str


@dataclass
class FTItem:
    """FTItem class."""

    id: str
    name: str = ""
    href: str = ""
    type: dict = field(default_factory=dict)
    division: dict = field(default_factory=dict)


@dataclass
class FTLinkItem:
    """FTLinkItem class."""

    name: str
    href: str = ""


@dataclass
class FTAccessZoneCommands:
    """FTAccessZone commands base class."""

    free: FTItemReference
    freePin: FTItemReference
    secure: FTItemReference
    securePin: FTItemReference
    codeOnly: FTItemReference
    codeOnlyPin: FTItemReference
    dualAuth: FTItemReference
    dualAuthPin: FTItemReference
    forgiveAntiPassback: FTItemReference | None
    setZoneCount: FTItemReference | None
    lockDown: FTItemReference
    cancelLockDown: FTItemReference
    cancel: FTItemReference


@dataclass
class FTAccessZone:
    """FTAccessZone item base class."""

    id: str
    href: str
    name: str
    description: str | None
    division: FTItem | None
    doors: list[FTLinkItem] | None
    zoneCount: int | None
    notes: str | None
    shortName: str | None
    updates: FTItemReference | None
    statusFlags: list[str] | None
    connectedController: FTItem | None
    commands: FTAccessZoneCommands | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTAccessZone:
        """Return FTAccessZone object from dict."""
        return from_dict(data_class=FTAccessZone, data=kwargs)


@dataclass
class FTAlarmZoneCommands:
    """FTAlarmZone commands base class."""

    arm: FTItemReference
    disarm: FTItemReference
    user1: FTItemReference
    user2: FTItemReference
    armHighVoltage: FTItemReference | None
    armLowFeel: FTItemReference | None
    cancel: FTItemReference | None


@dataclass
class FTAlarmZone:
    """FTAlarmZone item base class."""

    id: str
    href: str
    name: str
    description: str | None
    division: FTItem | None
    shortName: str | None
    notes: str | None
    updates: FTItemReference | None
    statusFlags: list[str] | None
    connectedController: FTItem | None
    commands: FTAlarmZoneCommands | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTAlarmZone:
        """Return FTAlarmZone object from dict."""
        return from_dict(data_class=FTAlarmZone, data=kwargs)


@dataclass
class FTFenceZoneCommands:
    """FTFenceZone commands base class."""

    on: FTItemReference
    off: FTItemReference
    shunt: FTItemReference
    unshunt: FTItemReference
    highVoltage: FTItemReference
    lowFeel: FTItemReference
    cancel: FTItemReference


@dataclass
class FTFenceZone:
    """FTFenceZone item base class."""

    id: str
    href: str
    name: str
    description: str | None
    division: FTItem | None
    voltage: int | None
    shortName: str | None
    notes: str | None
    updates: FTItemReference | None
    statusFlags: list[str] | None
    connectedController: FTItem | None
    commands: FTFenceZoneCommands | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTFenceZone:
        """Return FTAlarmZone object from dict."""
        return from_dict(data_class=FTFenceZone, data=kwargs)


@dataclass
class FTInputCommands:
    """FTInput commands base class."""

    shunt: FTItemReference
    unshunt: FTItemReference
    isolate: FTItemReference | None
    deisolate: FTItemReference | None


@dataclass
class FTInput:
    """FTInput item base class."""

    id: str
    href: str
    name: str
    description: str | None
    division: FTItem | None
    shortName: str | None
    notes: str | None
    updates: FTItemReference | None
    statusFlags: list[str] | None
    connectedController: FTItem | None
    commands: FTInputCommands | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTInput:
        """Return FTInput object from dict."""
        return from_dict(data_class=FTInput, data=kwargs)


@dataclass
class FTOutputCommands:
    """FTOutput commands base class."""

    on: FTItemReference
    off: FTItemReference
    pulse: FTItemReference
    cancel: FTItemReference


@dataclass
class FTOutput:
    """FTOutput item base class."""

    id: str
    href: str
    name: str
    description: str | None
    division: FTItem | None
    shortName: str | None
    notes: str | None
    updates: FTItemReference | None
    statusFlags: list[str] | None
    connectedController: FTItem | None
    commands: FTOutputCommands | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTOutput:
        """Return FTOutput object from dict."""
        return from_dict(data_class=FTOutput, data=kwargs)


@dataclass
class FTAccessGroup:
    """FTAccessGroup item base class."""

    id: str
    href: str
    name: str
    description: str | None
    parent: FTLinkItem | None
    division: FTItem | None
    cardholders: FTItemReference | None
    serverDisplayName: str | None
    children: list[FTLinkItem] | None
    personalDataDefinitions: list[FTLinkItem] | None
    visitor: bool | None
    escortVisitors: bool | None
    lockUnlockAccessZones: bool | None
    enterDuringLockdown: bool | None
    firstCardUnlock: bool | None
    overrideAperioPrivacy: bool | None
    aperioOfflineAccess: bool | None
    disarmAlarmZones: bool | None
    armAlarmZones: bool | None
    hvLfFenceZones: bool | None
    viewAlarms: bool | None
    shunt: bool | None
    lockOutFenceZones: bool | None
    cancelFenceZoneLockout: bool | None
    ackAll: bool | None
    ackBelowHigh: bool | None
    selectAlarmZone: bool | None
    armWhileAlarm: bool | None
    armWhileActiveAlarm: bool | None
    isolateAlarmZones: bool | None
    access: list[FTLinkItem] | None
    alarmZones: list[FTLinkItem] | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTAccessGroup:
        """Return FTAccessGroup object from dict."""
        return from_dict(data_class=FTAccessGroup, data=kwargs)


@dataclass
class FTAccessGroupMembership:
    """FTAccessGroupMembership base class."""

    href: str = ""
    status: FTStatus = field(init=False)
    accessGroup: FTLinkItem = field(init=False)
    active_from: datetime = field(init=False)
    active_until: datetime = field(init=False)

    @property
    def to_dict(self) -> dict[str, Any]:
        """Return json string for post and update."""
        _dict: dict[str, Any] = {}
        if self.href:
            _dict["href"] = self.href
        if getattr(self, "accessGroup", None) is not None:
            _dict["accessGroup"] = {"href": self.accessGroup.href}
        if getattr(self, "active_from", None) is not None:
            _dict["from"] = f"{self.active_from.isoformat()}Z"
        if getattr(self, "active_until", None) is not None:
            _dict["until"] = f"{self.active_until.isoformat()}Z"
        return _dict

    @classmethod
    def add_membership(
        cls,
        access_group: FTAccessGroup,
        active_from: datetime | None = None,
        active_until: datetime | None = None,
    ) -> FTAccessGroupMembership:
        """Create an FTAccessGroup item to assign."""
        _cls = FTAccessGroupMembership()
        _cls.accessGroup = FTLinkItem(name=access_group.name, href=access_group.href)
        if active_from:
            _cls.active_from = active_from
        if active_until:
            _cls.active_until = active_until
        return _cls

    @classmethod
    def update_membership(
        cls,
        access_group: FTAccessGroupMembership,
        active_from: datetime | None = None,
        active_until: datetime | None = None,
    ) -> FTAccessGroupMembership:
        """Create an FTAccessGroup update item."""
        _cls = FTAccessGroupMembership(href=access_group.href)
        if active_from:
            _cls.active_from = active_from
        if active_until:
            _cls.active_until = active_until
        return _cls

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTAccessGroupMembership:
        """Return FTAccessGroupMembership object from dict."""
        _cls = FTAccessGroupMembership(href=kwargs["href"])

        if status := kwargs.get("status"):
            _cls.status = FTStatus(**status)
        if accessGroup := kwargs.get("accessGroup"):
            _cls.accessGroup = FTLinkItem(**accessGroup)
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
    href: str = field(init=False)
    number: str = field(init=False)
    cardSerialNumber: str = field(init=False)
    issueLevel: int = field(init=False)
    status: FTStatus = field(init=False)
    active_from: datetime = field(init=False)
    active_until: datetime = field(init=False)

    @property
    def to_dict(self) -> dict[str, Any]:
        """Return json string for post and update."""
        _dict: dict[str, Any] = {"type": {"href": self.type.href}}
        _dict["href"] = self.href
        if number := getattr(self, "number", None):
            _dict["number"] = number
        if issueLevel := getattr(self, "issueLevel", None):
            _dict["issueLevel"] = issueLevel
        if active_from := getattr(self, "active_from", None):
            _dict["from"] = f"{active_from.isoformat()}Z"
        if active_until := getattr(self, "active_until", None):
            _dict["until"] = f"{active_until.isoformat()}Z"
        if status := getattr(self, "status", None):
            _dict["status"] = status
        return _dict

    @classmethod
    def create_card(
        cls,
        card_type: FTItem,
        number: str = "",
        issueLevel: int | None = None,
        active_from: datetime | None = None,
        active_until: datetime | None = None,
    ) -> FTCardholderCard:
        """Create an FTCardholder card object."""
        _cls = FTCardholderCard(type=card_type)
        if number:
            _cls.number = number
        if issueLevel:
            _cls.issueLevel = issueLevel
        if active_from:
            _cls.active_from = active_from
        if active_until:
            _cls.active_until = active_until
        return _cls

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTCardholderCard:
        """Return FTCardholderCard object from dict."""
        _cls = FTCardholderCard(type=FTLinkItem(**kwargs["type"]))
        _cls.href = kwargs["href"]
        if number := kwargs.get("number"):
            _cls.number = number
        _cls.issueLevel = cast(int, kwargs.get("issueLevel"))

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


@dataclass(init=False)
class FTPersonalDataFieldDefinition:
    """FTPersonalDataFieldDefinition class."""

    id: str
    name: str
    description: str
    type: str
    division: FTItem | None = None
    default: str = ""
    href: str = ""
    required: bool = False
    unique: bool = False
    accessGroups: list[FTLinkItem] = field(default_factory=list)
    regex: str = ""
    regexDescription: str = ""
    contentType: str = ""
    isProfileImage: bool = False

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTPersonalDataFieldDefinition:
        """Return FTPersonalDataFieldDefinition object from dict."""
        _cls = FTPersonalDataFieldDefinition()
        for key, value in kwargs.items():
            if not isinstance(value, dict | list):
                setattr(_cls, key, value)
            if key == "division" and isinstance(value, dict):
                _cls.division = FTItem(**value)
            if key == "accessGroups":
                _cls.accessGroups = [FTLinkItem(**group) for group in value]
        return _cls


# Cardholder models
@dataclass
class FTCardholderPdfDefinition:
    """FTCardholderPdfDefinition class."""

    id: str
    name: str
    href: str
    type: str


@dataclass
class FTCardholderPdfValue:
    """FTCardholderPdfValue class."""

    name: str
    href: str = ""
    value: str | FTItemReference = field(init=False)
    notifications: bool = field(init=False)
    definition: FTCardholderPdfDefinition = field(init=False)

    @property
    def to_dict(self) -> dict[str, Any]:
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
    def from_dict(
        cls, kwargs: list[dict[str, dict[str, Any]]]
    ) -> list[dict[str, FTCardholderPdfValue]]:
        """Return FTCardholderPdfValue object from dict."""
        pdf_values: list[dict[str, FTCardholderPdfValue]] = []
        for pdf_value in kwargs:
            for name, info in pdf_value.items():
                _cls = FTCardholderPdfValue(name=name[1:])
                if value := info.get("value"):
                    _cls.value = (
                        FTItemReference(**value) if isinstance(value, dict) else value
                    )
                if definition := info.get("definition"):
                    _cls.definition = FTCardholderPdfDefinition(**definition)
                if href := info.get("href"):
                    _cls.href = href
                if "notifications" in info:
                    _cls.notifications = info["notifications"]
                pdf_values.append({name[1:]: _cls})
        return pdf_values


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
        to_dict=lambda val: f"{val.isoformat()}Z",
    ),
    FTCardholderField(
        name="lastSuccessfulAccessZone",
        from_dict=lambda val: FTLinkItem(**val),
    ),
    FTCardholderField(name="serverDisplayName"),
    FTCardholderField(name="division", from_dict=lambda val: FTItem(**val)),
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
        from_dict=lambda val: FTCardholderPdfValue.from_dict(val),
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
        to_dict=lambda val: [access_group.to_dict for access_group in val],
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
    # FTCardholderField(name="edit", from_dict=lambda val: FTItemReference(**val)),
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
    firstName: str = ""
    lastName: str = ""
    shortName: str = ""
    description: str = ""
    authorised: bool = field(default=False)
    pdfs: dict[str, Any] = field(default_factory=dict)
    lastSuccessfulAccessTime: datetime = field(init=False)
    lastSuccessfulAccessZone: FTLinkItem = field(init=False)
    serverDisplayName: str = field(init=False)
    disableCipherPad: bool = field(default=False)
    usercode: str = ""
    operatorLoginEnabled: bool = field(default=False)
    operatorUsername: str = ""
    operatorPassword: str = ""
    operatorPasswordExpired: bool = field(default=False)
    windowsLoginEnabled: bool = field(default=False)
    windowsUsername: str = ""
    personalDataDefinitions: list[dict[str, FTCardholderPdfValue]] | None = field(
        default=None
    )
    cards: list[FTCardholderCard] | dict[str, list[FTCardholderCard]] | None = None
    accessGroups: list[FTAccessGroupMembership] | dict[
        str, list[FTAccessGroupMembership]
    ] | None = None
    # operator_groups: str
    # competencies: str
    # edit: str
    updateLocation: FTItemReference | None = None
    notes: str = ""
    # relationships: Any | None = None
    lockers: Any | None = None
    elevatorGroups: Any | None = None
    lastPrintedOrEncodedTime: datetime | None = None
    lastPrintedOrEncodedIssueLevel: int | None = None
    # redactions: Any | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return serialized str."""
        _dict: dict[str, Any] = {}
        for cardholder_field in FTCARDHOLDER_FIELDS:
            if value := getattr(self, cardholder_field.name, None):
                if cardholder_field.name in [
                    "cards",
                    "accessGroups",
                ] and isinstance(value, dict):
                    _dict[cardholder_field.name] = {
                        key: cardholder_field.to_dict(val) for key, val in value.items()
                    }
                else:
                    _dict[cardholder_field.name] = cardholder_field.to_dict(value)

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

    @classmethod
    def patch(
        cls,
        cardholder: FTCardholder,
        add: list[FTCardholderCard | FTAccessGroupMembership] | None = None,
        update: list[FTCardholderCard | FTAccessGroupMembership] | None = None,
        remove: list[FTCardholderCard | FTAccessGroupMembership] | None = None,
        **kwargs: Any,
    ) -> FTCardholder:
        """Return FTCardholder object from dict."""
        # TODO handle all fields that require a patch action like cards, access groups...
        _cls = FTCardholder()
        _cls.href = cardholder.href
        _cls.cards = {}
        _cls.accessGroups = {}

        if add:
            for item in add:
                if isinstance(item, FTCardholderCard):
                    _cls.cards.setdefault("add", []).append(item)
                elif isinstance(item, FTAccessGroupMembership):
                    _cls.accessGroups.setdefault("add", []).append(item)
        if update:
            for item in update:
                if isinstance(item, FTCardholderCard):
                    _cls.cards.setdefault("update", []).append(item)
                elif isinstance(item, FTAccessGroupMembership):
                    _cls.accessGroups.setdefault("update", []).append(item)
        if remove:
            for item in remove:
                if isinstance(item, FTCardholderCard):
                    _cls.cards.setdefault("remove", []).append(item)

                elif isinstance(item, FTAccessGroupMembership):
                    _cls.accessGroups.setdefault("remove", []).append(item)

        for key, value in kwargs.items():
            try:
                setattr(_cls, key, value)
            except AttributeError as err:
                print(err)
                continue
        return _cls


# Alarm and event models
@dataclass
class FTAlarm:
    """FTAlarm summary class"""

    state: str
    href: str = ""


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
    href: str = ""
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


@dataclass
class EventPost:
    """FTEvent summary class."""

    eventType: FTItem
    priority: int | None = None
    time: datetime | None = None
    message: str | None = None
    details: str | None = None
    source: FTItemReference | None = None
    cardholder: FTItemReference | None = None
    operator: FTItemReference | None = None
    entryAccessZone: FTItemReference | None = None
    accessGroup: FTItemReference | None = None
    lockerBank: FTItemReference | None = None
    locker: FTItemReference | None = None
    door: FTItemReference | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a dict from Event object."""
        _dict: dict[str, Any] = {
            "type": {"href": self.eventType.href},
            "eventType": {"href": self.eventType.href},
        }
        if self.source is not None:
            _dict["source"] = {"href": self.source.href}
        if self.priority is not None:
            _dict["priority"] = self.priority
        if self.time is not None:
            _dict["time"] = f"{self.time.isoformat()}Z"
        if self.message is not None:
            _dict["message"] = self.message
        if self.details is not None:
            _dict["details"] = self.details
        if self.cardholder is not None:
            _dict["cardholder"] = {"href": self.cardholder.href}
        if self.operator is not None:
            _dict["operator"] = {"href": self.operator.href}
        if self.entryAccessZone is not None:
            _dict["entryAccessZone"] = {"href": self.entryAccessZone.href}
        if self.lockerBank is not None:
            _dict["lockerBank"] = {"href": self.lockerBank.href}
        if self.locker is not None:
            _dict["locker"] = {"href": self.locker.href}
        if self.door is not None:
            _dict["door"] = {"href": self.door.href}
        return _dict


# Door models


@dataclass
class FTDoorField:
    """Class to represent FTDoor field."""

    name: str
    from_dict: Callable[[Any], Any] = lambda val: val
    to_dict: Callable[[Any], Any] = lambda val: val


FTDOOR_FIELDS: tuple[FTDoorField, ...] = (
    FTDoorField(name="href"),
    FTDoorField(name="id"),
    FTDoorField(name="name"),
    FTDoorField(name="division", from_dict=lambda val: FTItem(**val)),
    FTDoorField(name="entryAccessZone", from_dict=lambda val: FTLinkItem(**val)),
    FTDoorField(name="notes"),
    FTDoorField(name="shortName"),
    FTDoorField(name="updates", from_dict=lambda val: FTItemReference(**val)),
    FTDoorField(name="statusFlags"),
    FTDoorField(
        name="commands",
        from_dict=lambda val: {
            command: FTItemReference(**value) for command, value in val
        },
    ),
    FTDoorField(name="connectedController", from_dict=lambda val: FTItem(**val)),
)


@dataclass(init=False)
class FTDoor:
    """FTDoor details class."""

    href: str
    id: str
    name: str
    description: str
    division: FTItemReference
    entryAccessZone: FTLinkItem
    notes: str
    shortName: str
    updates: FTItemReference
    statusFlags: list[str]
    commands: dict[str, FTItemReference]
    connectedController: FTItem

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTDoor:
        """Return FTDoor object from dict."""
        _cls = FTDoor()
        for door_field in FTDOOR_FIELDS:
            if value := kwargs.get(door_field.name):
                setattr(_cls, door_field.name, door_field.from_dict(value))
        return _cls


# Item status and overrides
@dataclass
class FTItemStatus:
    """Item status class."""

    id: str
    status: str
    statusText: str
    statusFlags: list[str]
