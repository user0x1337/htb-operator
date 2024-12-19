from datetime import datetime
from typing import Optional, List

from htbapi import client


class BadgeCategory(client.BaseHtbApiObject):
    name: str
    description: str
    badges: List["Badge"]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data["id"]
        self.name = data["name"]
        self.description = data["description"]
        if "badges" in data:
            self.badges = [Badge(_client=_client, data=x, _badge_category=self) for x in data["badges"]]
        else:
            self.badges = []

    def __repr__(self) -> str:
        return f"<BadgeCategory '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "badges": [x.to_dict() for x in self.badges],
        }


class Badge(client.BaseHtbApiObject):
    name: str
    description: str
    badge_obtained: bool
    badge_obtained_datetime : Optional[datetime]
    color: Optional[str]
    users_count: int
    rarity: float
    _badge_category: BadgeCategory

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", _badge_category: BadgeCategory):
        self._client = _client
        self.id = data["id"]
        self._badge_category = _badge_category
        self.name = data["name"]
        self.description = data["description_en"]
        self.color = data.get("color")
        self.users_count = data["users_count"]
        self.rarity = data["rarity"]
        self.badge_obtained = False
        self.badge_obtained_datetime = None

    def set_badge_obtained(self, badge_obtained: bool, when: datetime):
        assert badge_obtained is not None

        self.badge_obtained = badge_obtained
        self.badge_obtained_datetime = when

    def __repr__(self) -> str:
        return f"<Badge '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "users_count": self.users_count,
            "rarity": self.rarity,
            "badge_obtained": self.badge_obtained,
            "badge_obtained_datetime": self.badge_obtained_datetime,
        }
