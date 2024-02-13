from dataclasses import asdict, dataclass
from typing import Any
from dacite import from_dict


@dataclass
class FTAccessGroupMembership:
    """FTAccessGroupMembership base class."""

    href: str | None
    status: str | None
    accessGroup: str | None
    active_from: str | None
    active_until: str | None

    @property
    def to_dict(self) -> dict[str, Any]:
        """Return json string for post and update."""
        print(asdict(self, ignore_default=True))
        # _dict: dict[str, Any] = {}
        # if self.href:
        #     _dict["href"] = self.href
        # if self.accessGroup:
        #     _dict["accessGroup"] = {"href": self.accessGroup.href}
        # if self.active_from:
        #     _dict["from"] = f"{self.active_from.isoformat()}Z"
        # if self.active_until:
        #     _dict["until"] = f"{self.active_until.isoformat()}Z"
        # return _dict


test = from_dict(FTAccessGroupMembership, {"status": "1"})
print(test.to_dict)
