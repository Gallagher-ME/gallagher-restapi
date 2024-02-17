"""Gallagher item models."""
from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Type, TypeVar

import pytz
from dacite import Config, from_dict

T = TypeVar("T")


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

    accessGroups: dict[str, Any] | None
    accessZones: dict[str, Any] | None
    alarms: dict[str, Any] | None
    alarmZones: dict[str, Any] | None
    cardholders: dict[str, Any] | None
    cardTypes: dict[str, Any] | None
    competencies: dict[str, Any] | None
    dayCategories: dict[str, Any] | None
    divisions: dict[str, Any] | None
    doors: dict[str, Any] | None
    elevators: dict[str, Any] | None
    events: dict[str, Any] | None
    fenceZones: dict[str, Any] | None
    inputs: dict[str, Any] | None
    interlockGroups: dict[str, Any] | None
    items: dict[str, Any] | None
    lockerBanks: dict[str, Any] | None
    macros: dict[str, Any] | None
    operatorGroups: dict[str, Any] | None
    outputs: dict[str, Any] | None
    personalDataFields: dict[str, Any] | None
    receptions: dict[str, Any] | None
    roles: dict[str, Any] | None
    schedules: dict[str, Any] | None
    visits: dict[str, Any] | None

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

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTApiFeatures:
        """Return FTApiFeatures object from dict."""
        return from_dict(data_class=FTApiFeatures, data=kwargs)


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
    href: str | None


# region Access zone models


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
        return from_dict(
            data_class=FTAccessZone,
            data=kwargs,
            config=Config(type_hooks=CONVERTERS),
        )


# endregion Access zone models

# region Alarm zone models


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
        return from_dict(
            data_class=FTAlarmZone,
            data=kwargs,
            config=Config(type_hooks=CONVERTERS),
        )


# endregion Alarm zone models

# region Fence zone models


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
        return from_dict(
            data_class=FTFenceZone,
            data=kwargs,
            config=Config(type_hooks=CONVERTERS),
        )


# endregion Fence zone models


# region Input models
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
        return from_dict(
            data_class=FTInput,
            data=kwargs,
            config=Config(type_hooks=CONVERTERS),
        )


# endregion Input models


# region Output models
@dataclass
class FTOutputCommands:
    """FTOutput commands base class."""

    on: FTItemReference
    off: FTItemReference
    pulse: FTItemReference | None
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
        return from_dict(
            data_class=FTOutput,
            data=kwargs,
            config=Config(type_hooks=CONVERTERS),
        )


# endregion Output models

# region Access groups models


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

    href: str | None
    status: FTStatus | None
    accessGroup: FTLinkItem | None
    active_from: datetime | None
    active_until: datetime | None

    @property
    def to_dict(self) -> dict[str, Any]:
        """Return json string for post and update."""
        _dict: dict[str, Any] = {}
        if self.href:
            _dict["href"] = self.href
        if self.accessGroup:
            _dict["accessGroup"] = {"href": self.accessGroup.href}
        if self.active_from:
            _dict["from"] = f"{self.active_from.isoformat()}Z"
        if self.active_until:
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
        kwargs: dict[str, Any] = {
            "accessGroup": {"name": access_group.name, "href": access_group.href}
        }
        if active_from:
            kwargs["active_from"] = active_from
        if active_until:
            kwargs["active_until"] = active_until
        return from_dict(FTAccessGroupMembership, kwargs)

    @classmethod
    def update_membership(
        cls,
        access_group_membership: FTAccessGroupMembership,
        active_from: datetime | None = None,
        active_until: datetime | None = None,
    ) -> FTAccessGroupMembership:
        """Create an FTAccessGroup update item."""
        kwargs: dict[str, Any] = {"href": access_group_membership.href}
        if active_from:
            kwargs["active_from"] = active_from
        if active_until:
            kwargs["active_until"] = active_until
        return from_dict(FTAccessGroupMembership, kwargs)

    @classmethod
    def from_dict(cls, kwargs: list[dict[str, Any]]) -> list[FTAccessGroupMembership]:
        """Return FTAccessGroupMembership object from dict."""
        return [
            from_dict(
                FTAccessGroupMembership,
                access_group,
                config=Config(type_hooks=CONVERTERS),
            )
            for access_group in kwargs
        ]


# endregion Access groups models


# region Card type models
@dataclass
class FTCardType:
    """FTCardType item base class."""

    href: str
    id: str
    name: str
    division: FTItem | None
    notes: str | None
    facilityCode: str
    availableCardStates: list[str] | None
    credentialClass: str | None
    minimumNumber: str | None
    maximumNumber: str | None
    serverDisplayName: str | None
    regex: str | None
    regexDescription: str | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTCardType:
        """Return FTCardType object from dict."""
        return from_dict(data_class=FTCardType, data=kwargs)


# endregion Card type models

# region Cardholder card models


@dataclass
class FTCardholderCard:
    """FTCardholder card base class."""

    type: FTLinkItem | FTItemReference
    href: str | None
    number: str | None
    cardSerialNumber: str | None
    issueLevel: int | None
    status: FTStatus | None
    from_: datetime | None
    until: datetime | None

    @property
    def to_dict(self) -> dict[str, Any]:
        """Return json string for post and update."""
        _dict: dict[str, Any] = {"type": {"href": self.type.href}}
        if self.href:
            _dict["href"] = self.href
        if self.number:
            _dict["number"] = self.number
        if self.issueLevel:
            _dict["issueLevel"] = self.issueLevel
        if self.from_:
            _dict["from"] = f"{self.from_.isoformat()}Z"
        if self.until:
            _dict["until"] = f"{self.until.isoformat()}Z"
        if self.status:
            _dict["status"] = self.status
        return _dict

    @classmethod
    def create_card(
        cls,
        card_type_href: str,
        number: str = "",
        issueLevel: int | None = None,
        active_from: datetime | None = None,
        active_until: datetime | None = None,
    ) -> FTCardholderCard:
        """Create an FTCardholder card object."""
        kwargs: dict[str, Any] = {"type": {"href": card_type_href}}
        if number:
            kwargs["number"] = number
        if issueLevel:
            kwargs["issueLevel"] = issueLevel
        if active_from:
            kwargs["from_"] = active_from
        if active_until:
            kwargs["until"] = active_until
        return from_dict(FTCardholderCard, kwargs)

    @classmethod
    def from_dict(cls, kwargs: list[dict[str, Any]]) -> list[FTCardholderCard]:
        """Return FTCardholderCard object from dict."""
        print(kwargs)
        return [
            from_dict(FTCardholderCard, card, config=Config(type_hooks=CONVERTERS))
            for card in kwargs
        ]


# endregion Cardholder card models

# region PDF definition models


@dataclass
class FTPersonalDataFieldDefinition:
    """FTPersonalDataFieldDefinition class."""

    id: str
    href: str
    name: str
    serverDisplayName: str | None
    description: str | None
    type: str | None
    division: FTItem | None
    default: str | None
    defaultAccess: str | None
    operatorAccess: str | None
    sortPriority: int | None
    accessGroups: list[FTLinkItem] | None
    regex: str | None
    regexDescription: str | None
    contentType: str | None
    isProfileImage: bool = False
    required: bool = False
    unique: bool = False

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTPersonalDataFieldDefinition:
        """Return FTPersonalDataFieldDefinition object from dict."""
        return from_dict(FTPersonalDataFieldDefinition, kwargs)


# endregion pdf definition models


# region Cardholder models
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
    href: str | None
    definition: FTCardholderPdfDefinition | None
    value: int | str | FTItemReference | None
    notifications: bool | None

    @property
    def to_dict(self) -> dict[str, Any]:
        """Return json string for post and update."""
        return {f"@{self.name}": {"notifications": self.notifications}}

    @classmethod
    def create_pdf(
        cls,
        pdf_definition: FTPersonalDataFieldDefinition,
        value: str,
        enable_notification: bool = False,
    ) -> FTCardholderPdfValue:
        """Create FTCardholderPdfValue object for POST."""
        kwargs: dict[str, Any] = {"name": pdf_definition.name}
        kwargs["value"] = value
        kwargs["notifications"] = enable_notification
        return from_dict(FTCardholderPdfValue, kwargs)

    @classmethod
    def from_dict(
        cls, kwargs: list[dict[str, dict[str, Any]]]
    ) -> list[dict[str, FTCardholderPdfValue]]:
        """Return FTCardholderPdfValue object from dict."""
        pdf_values: list[dict[str, FTCardholderPdfValue]] = []
        for pdf in kwargs:
            for name, info in pdf.items():
                name = name[1:]
                pdf_value = from_dict(FTCardholderPdfValue, {"name": name, **info})
                pdf_values.append({name: pdf_value})
        return pdf_values


@dataclass
class FTCardholder:
    """FTCardholder details class."""

    href: str
    id: str
    division: FTItemReference | None
    name: str | None
    firstName: str | None
    lastName: str | None
    shortName: str | None
    description: str | None
    lastSuccessfulAccessTime: datetime | None
    lastSuccessfulAccessZone: FTLinkItem | None
    serverDisplayName: str | None
    disableCipherPad: bool | None
    usercode: str | None
    operatorUsername: str | None
    operatorPassword: str | None
    windowsUsername: str | None
    personalDataDefinitions: list[dict[str, FTCardholderPdfValue]] | None
    cards: list[FTCardholderCard] | dict[str, list[FTCardholderCard]] | None
    accessGroups: list[FTAccessGroupMembership] | dict[
        str, list[FTAccessGroupMembership]
    ] | None
    # operator_groups: str
    # competencies: str
    # edit: str
    updateLocation: FTItemReference | None
    notes: str | None
    # relationships: Any | None
    lockers: Any | None
    elevatorGroups: Any | None
    lastPrintedOrEncodedTime: datetime | None
    lastPrintedOrEncodedIssueLevel: int | None
    # redactions: Any | None
    pdfs: dict[str, str | FTItemReference] = field(default_factory=dict)
    authorised: bool = False
    operatorLoginEnabled: bool = False
    operatorPasswordExpired: bool = False
    windowsLoginEnabled: bool = False

    def as_dict(self) -> dict[str, Any]:
        """Return serialized str."""
        _dict: dict[str, Any] = {
            key: value
            for key, value in self.__dict__.items()
            if key != "pdfs" and value is not None
        }
        if self.pdfs:
            _dict.update({f"@{name}": value for name, value in self.pdfs.items()})
        return json.loads(json.dumps(_dict, default=json_serializer))

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTCardholder:
        """Return FTCardholder object from dict."""
        cardholder = from_dict(
            FTCardholder, kwargs, config=Config(type_hooks=CONVERTERS)
        )
        for cardholder_pdf, value in list(kwargs.items()):
            if cardholder_pdf.startswith("@"):
                value = FTItemReference(**value) if isinstance(value, dict) else value
                cardholder.pdfs[cardholder_pdf[1:]] = value

        return cardholder


@dataclass
class FTNewCardholder:
    """FTNewCardholder object class."""

    division: FTItemReference
    firstName: str | None = None
    lastName: str | None = None
    shortName: str | None = None
    description: str | None = None
    usercode: str | None = None
    operatorUsername: str | None = None
    operatorPassword: str | None = None
    windowsUsername: str | None = None
    personalDataDefinitions: list[dict[str, FTCardholderPdfValue]] | None = None
    cards: list[FTCardholderCard] | dict[str, list[FTCardholderCard]] | None = None
    accessGroups: list[FTAccessGroupMembership] | dict[
        str, list[FTAccessGroupMembership]
    ] | None = None
    notes: str | None = None
    lockers: Any | None = None
    elevatorGroups: Any | None = None
    pdfs: dict[str, Any] = field(default_factory=dict)
    authorised: bool | None = None
    operatorLoginEnabled: bool | None = None
    operatorPasswordExpired: bool | None = None
    windowsLoginEnabled: bool | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return serialized str."""
        _dict: dict[str, Any] = {
            key: value
            for key, value in self.__dict__.items()
            if key != "pdfs" and value is not None
        }
        if self.pdfs:
            _dict.update({f"@{name}": value for name, value in self.pdfs.items()})
        return json.loads(json.dumps(_dict, default=json_serializer))

    def patch(
        self,
        add: list[FTCardholderCard | FTAccessGroupMembership] | None = None,
        update: list[FTCardholderCard | FTAccessGroupMembership] | None = None,
        remove: list[FTCardholderCard | FTAccessGroupMembership] | None = None,
        **kwargs: Any,
    ) -> None:
        """Return FTCardholder object from dict."""
        self.cards = {}
        self.accessGroups = {}
        if add:
            for item in add:
                if isinstance(item, FTCardholderCard):
                    self.cards.setdefault("add", []).append(item)
                elif isinstance(item, FTAccessGroupMembership):
                    self.accessGroups.setdefault("add", []).append(item)
        if update:
            for item in update:
                if isinstance(item, FTCardholderCard):
                    self.cards.setdefault("update", []).append(item)
                elif isinstance(item, FTAccessGroupMembership):
                    self.accessGroups.setdefault("update", []).append(item)
        if remove:
            for item in remove:
                if isinstance(item, FTCardholderCard):
                    self.cards.setdefault("remove", []).append(item)

                elif isinstance(item, FTAccessGroupMembership):
                    self.accessGroups.setdefault("remove", []).append(item)

        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except AttributeError:
                continue


# endregion Cardholder models


# region Alarm and event models
@dataclass
class FTAlarm:
    """FTAlarm summary class"""

    state: str
    href: str = ""


@dataclass
class FTEventCard:
    """Event card details."""

    number: str
    issueLevel: int
    facilityCode: str

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTEventCard:
        """Return Event card object from dict."""
        return from_dict(FTEventCard, kwargs)


@dataclass
class FTEventGroup:
    """FTEvent group class."""

    id: str
    name: str
    href: str
    eventTypes: list[FTItem]

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTEventGroup:
        """Return Event card object from dict."""
        return from_dict(FTEventGroup, kwargs)


@dataclass
class EventField:
    """Class to represent Event field."""

    key: str
    name: str
    value: Callable[[Any], Any] = lambda val: val


@dataclass
class FTEvent:
    """FTEvent summary class."""

    href: str
    id: str
    serverDisplayName: str | None
    time: datetime
    message: str
    occurrences: int | None
    priority: int
    alarm: FTAlarm | None
    operator: FTLinkItem | None
    source: FTItem
    group: FTItemType
    type: FTItemType
    eventType: FTItemType | None
    division: FTItem
    cardholder: FTCardholder | None  # check converter
    entryAccessZone: FTItem
    exitAccessZone: FTItem
    door: FTLinkItem | None
    accessGroup: FTItemReference | None
    card: FTEventCard | None
    lastOccurrenceTime: datetime | None
    details: str | None
    previous: FTItemReference | None
    next: FTItemReference | None
    updates: FTItemReference | None
    # modified_item: str

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTEvent:
        """Return FTEvent object from dict."""
        return from_dict(FTEvent, kwargs, config=Config(type_hooks=CONVERTERS))


@dataclass
class EventFilter:
    """Event filter class."""

    top: int | None = None
    after: datetime | None = None
    before: datetime | None = None
    sources: list[str] | None = None
    event_types: list[str] | None = None
    event_groups: list[str] | None = None
    cardholders: list[str] | None = None
    divisions: list[str] | None = None
    related_items: list[str] | None = None
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
            params["source"] = ",".join(self.sources)
        if self.event_types:
            params["type"] = ",".join(self.event_types)
        if self.event_groups:
            params["group"] = ",".join(self.event_groups)
        if self.cardholders:
            params["cardholder"] = ",".join(self.cardholders)
        if self.divisions:
            params["division"] = ",".join(self.divisions)
        if self.related_items:
            params["relatedItem"] = ",".join(self.related_items)
        if self.fields:
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


# endregion Alarm and event models


# region Door models
@dataclass
class FTDoorCommands:
    """FTDoor commands base class."""

    open: FTItemReference


@dataclass
class FTDoor:
    """FTDoor details class."""

    href: str
    id: str
    name: str
    description: str | None
    division: FTItemReference | None
    entryAccessZone: FTLinkItem | None
    notes: str | None
    shortName: str | None
    updates: FTItemReference | None
    statusFlags: list[str] | None
    commands: FTDoorCommands | None
    connectedController: FTItem | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTDoor:
        """Return FTDoor object from dict."""
        return from_dict(
            data_class=FTDoor, data=kwargs, config=Config(type_hooks=CONVERTERS)
        )


# endregion Door models


# region Item status and overrides
@dataclass
class FTItemStatus:
    """Item status class."""

    id: str
    status: str
    statusText: str
    statusFlags: list[str]


# endregion Item status and overrides

CONVERTERS: dict[Any, Callable[[Any], Any]] = {
    datetime: lambda x: datetime.fromisoformat(x[:-1]).replace(tzinfo=pytz.utc),  # type: ignore[index]
    FTAccessZoneCommands: lambda x: verify_commands(FTAccessZoneCommands, x),
    FTAlarmZoneCommands: lambda x: verify_commands(FTAlarmZoneCommands, x),
    FTDoorCommands: lambda x: verify_commands(FTDoorCommands, x),
    FTInputCommands: lambda x: verify_commands(FTInputCommands, x),
    FTOutputCommands: lambda x: verify_commands(FTOutputCommands, x),
    FTCardholder: FTCardholder.from_dict,
    list[dict[str, FTCardholderPdfValue]]: FTCardholderPdfValue.from_dict,
    list[FTCardholderCard]: FTCardholderCard.from_dict,
    list[FTAccessGroupMembership]: FTAccessGroupMembership.from_dict,
}


def verify_commands(cls: Type[T], kwargs: dict[str, Any]) -> T | None:
    """Verify that commands are not disabled."""
    for commands in kwargs.values():
        if "disabled" in commands:
            return None
    return from_dict(data_class=cls, data=kwargs)


def json_serializer(value: Any) -> Any:
    """serialize dataclass objects."""
    if to_dict := getattr(value, "to_dict", None):
        return to_dict
    return value.__dict__
