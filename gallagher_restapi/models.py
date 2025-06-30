"""Gallagher item models."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import StrEnum
from typing import Any, Type, TypeVar

import pytz
from dacite import Config, from_dict

from gallagher_restapi.exceptions import LicenseError

T = TypeVar("T")

MOVEMENT_EVENT_TYPES = ["20001", "20002", "20003", "20047", "20107", "42415"]


class HTTPMethods(StrEnum):
    """HTTP Methods class."""

    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"


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
    lockers: dict[str, Any] | None

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
        except ValueError as err:
            raise ValueError("Incorrect syntax of feature.") from err
        if not hasattr(self, main_feature):
            raise ValueError(f"{main_feature} is not a valid feature")
        if not (feature := getattr(self, main_feature)):
            raise LicenseError(f"{main_feature} is not licensed for this site.")
        if sub_feature and sub_feature not in feature:
            raise ValueError(f"{sub_feature} is not found in {main_feature}")
        return feature[sub_feature or main_feature]["href"]

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
    extra_fields: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTItem:
        """Return FTItem object from dict."""
        _item = from_dict(data_class=FTItem, data=kwargs)
        cls_fields = set(f.name for f in fields(_item))
        _item.extra_fields = {k: v for k, v in kwargs.items() if k not in cls_fields}
        return _item


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

# region Operator groups models


@dataclass
class FTOperatorGroupMembership:
    """FTOperatorGroupMembership item base class."""

    cardholder: FTLinkItem
    href: str | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTOperatorGroupMembership:
        """Return list of FTOperatorGroupMembership objects from dict."""
        return from_dict(data_class=FTOperatorGroupMembership, data=kwargs)


@dataclass
class FTOperatorGroup:
    """FTOperatorGroup item base class."""

    href: str
    name: str
    description: str | None
    division: FTItem | None
    cardholders: FTItemReference | None
    serverDisplayName: str | None
    divisions: list[dict[str, FTLinkItem]] | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTOperatorGroup:
        """Return FTOperatorGroup object from dict."""
        return from_dict(data_class=FTOperatorGroup, data=kwargs)


# endregion Operator groups models


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
        return [
            from_dict(FTCardholderCard, card, config=Config(type_hooks=CONVERTERS))
            for card in kwargs
        ]


# endregion Cardholder card models

# region PDF definition models


class PDFType(StrEnum):
    """PDF types class."""

    STRING = "string"
    IMAGE = "image"
    STRENUM = "strEnum"
    NUMERIC = "numeric"
    DATE = "date"
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"
    MOBILE = "mobile"


@dataclass
class FTPersonalDataFieldDefinition:
    """FTPersonalDataFieldDefinition class."""

    id: str
    href: str
    name: str
    serverDisplayName: str | None
    description: str | None
    type: PDFType | None
    division: FTItem | None
    default: str | None
    defaultAccess: str | None
    operatorAccess: str | None
    sortPriority: int | None
    accessGroups: list[FTLinkItem] | None
    regex: str | None
    regexDescription: str | None
    contentType: str | None
    isProfileImage: bool | None
    required: bool | None
    unique: bool | None
    strEnumList: list[str] | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTPersonalDataFieldDefinition:
        """Return FTPersonalDataFieldDefinition object from dict."""
        return from_dict(
            FTPersonalDataFieldDefinition, kwargs, config=Config(cast=[PDFType])
        )


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

    href: str | None
    id: str | None
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
    accessGroups: (
        list[FTAccessGroupMembership] | dict[str, list[FTAccessGroupMembership]] | None
    )
    # operator_groups: str
    # competencies: str
    # edit: str
    updateLocation: FTItemReference | None
    notes: str | None
    # relationships: Any | None
    lockers: list[FTLockerMembership] | dict[str, list[FTLockerMembership]] | None
    elevatorGroups: Any | None
    lastPrintedOrEncodedTime: datetime | None
    lastPrintedOrEncodedIssueLevel: int | None
    # redactions: Any | None
    pdfs: dict[str, str | int | FTItemReference] = field(default_factory=dict)
    authorised: bool = False
    operatorLoginEnabled: bool = False
    operatorPasswordExpired: bool = False
    useExtendedAccessTime: bool = False
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

    division: FTItemReference | None = None
    firstName: str | None = None
    lastName: str | None = None
    shortName: str | None = None
    description: str | None = None
    usercode: str | None = None
    operatorUsername: str | None = None
    operatorPassword: str | None = None
    windowsUsername: str | None = None
    personalDataDefinitions: list[dict[str, FTCardholderPdfValue]] | None = None
    cards: list[FTCardholderCard] | dict[str, list[FTCardholderCard]] | None = field(
        default_factory=dict
    )
    accessGroups: (
        list[FTAccessGroupMembership] | dict[str, list[FTAccessGroupMembership]] | None
    ) = field(default_factory=dict)
    notes: str | None = None
    lockers: list[FTLockerMembership] | dict[str, list[FTLockerMembership]] | None = (
        field(default_factory=dict)
    )
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

    @classmethod
    def patch(
        cls,
        add: list[FTCardholderCard | FTAccessGroupMembership | FTLockerMembership]
        | None = None,
        update: list[FTCardholderCard | FTAccessGroupMembership | FTLockerMembership]
        | None = None,
        remove: list[FTCardholderCard | FTAccessGroupMembership | FTLockerMembership]
        | None = None,
        **kwargs: Any,
    ) -> FTNewCardholder:
        """Return FTCardholder object from dict."""
        _cls = FTNewCardholder()
        attr_class = {
            "FTCardholderCard": "cards",
            "FTAccessGroupMembership": "accessGroups",
            "FTLockerMembership": "lockers",
        }
        for action, items in {"add": add, "update": update, "remove": remove}.items():
            for item in items or []:
                if (item_type := type(item).__name__) not in attr_class:
                    continue
                getattr(_cls, attr_class[item_type]).setdefault(action, []).append(item)

        for key, value in kwargs.items():
            try:
                setattr(_cls, key, value)
            except AttributeError:
                continue
        return _cls


class CardholderChangeType(StrEnum):
    """Cardholder change types."""

    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"


@dataclass
class CardholderChange:
    """Cardholder changes object class."""

    time: datetime | None
    type: CardholderChangeType | None
    item: FTItemReference | None
    oldValues: dict[str, Any] | None
    newValues: dict[str, Any] | None
    cardholder: FTCardholder | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> CardholderChange:
        """Return list of cardholder changes object from json."""
        return from_dict(
            CardholderChange,
            kwargs,
            config=Config(cast=[CardholderChangeType], type_hooks=CONVERTERS),
        )


# endregion Cardholder models


# region Alarm and event models


class FTAlarmState(StrEnum):
    """Alarm states."""

    UNACKNOWLEDGED = "unacknowledged"
    ACKNOWLEDGED = "acknowledged"
    PROCESSED = "processed"


@dataclass
class FTEventAlarm:
    """FTAlarm summary class"""

    state: FTAlarmState
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
class FTEventBase:
    """FTEventBase class."""

    href: str
    id: str
    time: datetime
    message: str
    source: FTItem
    type: FTItemType | str
    eventType: FTItemType | None
    priority: int
    division: FTItem | None


@dataclass
class FTAlarm(FTEventBase):
    """FTAlarm class."""

    state: FTAlarmState
    active: bool
    event: FTItemReference | None
    notePresets: list[str] | None
    view: FTItemReference
    comment: FTItemReference
    acknowledge: FTItemReference | None
    acknowledgeWithComment: FTItemReference | None
    process: FTItemReference | None
    processWithComment: FTItemReference | None
    forceProcess: FTItemReference | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTAlarm:
        """Return FTAlarm object from dict."""
        return from_dict(
            FTAlarm, kwargs, config=Config(cast=[FTAlarmState], type_hooks=CONVERTERS)
        )


@dataclass
class FTEvent(FTEventBase):
    """FTEvent class."""

    serverDisplayName: str | None
    occurrences: int | None
    alarm: FTEventAlarm | None
    operator: FTLinkItem | None
    group: FTItemType
    cardholder: FTCardholder | None
    entryAccessZone: FTItem | None
    exitAccessZone: FTItem | None
    door: FTLinkItem | None
    accessGroup: FTItemReference | None
    card: FTEventCard | None
    lastOccurrenceTime: datetime | None
    details: str | None
    previous: FTItemReference | None
    next: FTItemReference | None
    updates: FTItemReference | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTEvent:
        """Return FTEvent object from dict."""
        return from_dict(
            FTEvent, kwargs, config=Config(cast=[FTAlarmState], type_hooks=CONVERTERS)
        )


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


# region Lockers models
@dataclass
class FTLockerCommands:
    """FTDoor commands base class."""

    open: FTItemReference
    quarantine: FTItemReference
    quarantineUntil: FTItemReference
    cancelQuarantine: FTItemReference


@dataclass
class LockerAssignment:
    """Locker assignment class."""

    href: str
    cardholder: FTLinkItem
    from_: datetime | None
    until: datetime | None

    @classmethod
    def from_dict(cls, kwargs: list[dict[str, Any]]) -> list[LockerAssignment]:
        """Return FTLocker object from dict."""
        return [
            from_dict(
                LockerAssignment,
                data=assignment,
                config=Config(type_hooks=CONVERTERS),
            )
            for assignment in kwargs
        ]


@dataclass
class FTLockerMembership:
    """Locker membership class."""

    href: str | None
    locker: FTLinkItem | None
    from_: datetime | None = None
    until: datetime | None = None

    @property
    def to_dic(self) -> dict[str, Any]:
        """Return a dict from object."""
        _dict: dict[str, Any] = {}
        if self.href:
            _dict["href"] = self.href
        if self.from_:
            _dict["from"] = f"{self.from_.isoformat()}Z"
        if self.until:
            _dict["until"] = f"{self.until.isoformat()}Z"
        return _dict

    @classmethod
    def add_membership(
        cls,
        locker: FTLocker,
        active_from: datetime | None = None,
        active_until: datetime | None = None,
    ) -> FTLockerMembership:
        """Create an FTLocker item to assign."""
        kwargs: dict[str, Any] = {"locker": {"name": locker.name, "href": locker.href}}
        if active_from:
            kwargs["active_from"] = active_from
        if active_until:
            kwargs["active_until"] = active_until
        return from_dict(FTLockerMembership, kwargs)

    @classmethod
    def from_dict(cls, kwargs: list[dict[str, Any]]) -> list[FTLockerMembership]:
        """Return FTLockerMembership object from dict."""
        return [
            from_dict(
                FTLockerMembership,
                locker,
                config=Config(type_hooks=CONVERTERS),
            )
            for locker in kwargs
        ]


@dataclass
class FTLocker:
    """Locker class."""

    id: str
    href: str
    name: str | None
    shortName: str | None
    description: str | None
    division: FTItem | None
    lockerBank: FTLinkItem | None
    connectedController: FTItem | None
    assignments: list[LockerAssignment] | None
    commands: FTLockerCommands | None

    @classmethod
    def from_list(cls, kwargs: list[dict[str, Any]]) -> list[FTLocker]:
        """Return list of FTLocker objects from dict."""
        return [
            from_dict(
                data_class=FTLocker, data=locker, config=Config(type_hooks=CONVERTERS)
            )
            for locker in kwargs
        ]

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTLocker:
        """Return FTLocker object from dict."""
        return from_dict(
            data_class=FTLocker, data=kwargs, config=Config(type_hooks=CONVERTERS)
        )


@dataclass
class FTLockerBank:
    """Locker Bank class."""

    id: str
    href: str
    name: str
    shortName: str | None
    description: str | None
    division: FTItem | None
    notes: str | None
    connectedController: FTItem | None
    lockers: list[FTLocker] | None
    updates: FTItemReference | None

    @classmethod
    def from_dict(cls, kwargs: dict[str, Any]) -> FTLockerBank:
        """Return FTLockerBank object from dict."""
        return from_dict(
            data_class=FTLockerBank, data=kwargs, config=Config(type_hooks=CONVERTERS)
        )


# endregion Lockers models

CONVERTERS: dict[Any, Callable[[Any], Any]] = {
    datetime: lambda x: datetime.fromisoformat(x[:-1]).replace(tzinfo=pytz.utc),  # type: ignore[index]
    FTAccessZoneCommands: lambda x: verify_commands(FTAccessZoneCommands, x),
    FTAlarmZoneCommands: lambda x: verify_commands(FTAlarmZoneCommands, x),
    FTDoorCommands: lambda x: verify_commands(FTDoorCommands, x),
    FTInputCommands: lambda x: verify_commands(FTInputCommands, x),
    FTOutputCommands: lambda x: verify_commands(FTOutputCommands, x),
    FTFenceZoneCommands: lambda x: verify_commands(FTFenceZoneCommands, x),
    FTCardholder: FTCardholder.from_dict,
    list[dict[str, FTCardholderPdfValue]]: FTCardholderPdfValue.from_dict,
    list[FTCardholderCard]: FTCardholderCard.from_dict,
    list[FTAccessGroupMembership]: FTAccessGroupMembership.from_dict,
    list[FTLocker]: FTLocker.from_list,
    list[LockerAssignment]: LockerAssignment.from_dict,
    FTLockerCommands: lambda x: verify_commands(FTLockerCommands, x),
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
