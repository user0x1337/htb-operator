from typing import List

from htbapi import client
from htbapi.base_user_profile import BaseUserProfile


class Company(client.BaseHtbApiObject):
    name: str
    description: str
    url: str
    image_url: str

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self.name = data.get('name')
        self.description = data.get('description')
        self.url = data.get('url')
        self.image_url = data.get('image')

    def __repr__(self):
        return f"<Company '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "ID": self.id,
            "description": self.description,
            "url": self.url,
            "image_url": self.image_url
        }

class FortressFlag(client.BaseHtbApiObject):
    title: str
    points: int
    owned: bool

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.title = data.get('title')
        self.points = data.get('points')
        self.owned = data.get('owned', False)

    def __repr__(self):
        return f"<FortressFlag '{self.title} | {self.id}'>"

    def to_dict(self):
        return {
            "ID": self.id,
            "title": self.title,
            "points": self.points,
            "owned": self.owned
        }

class Fortress(client.BaseHtbApiObject):
    """Fortress API object."""
    name: str
    ip: str
    company: Company
    reset_votes: int
    description: str
    completion_message: str
    progress_percent: float
    players_completed: int
    points: int
    flags: List[FortressFlag]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data['id']
        self.name = data['name']
        self.ip = data['ip']
        self.company = Company(data['company'], _client)
        self.reset_votes = data['reset_votes']
        self.description = data['description']
        self.completion_message = data['completion_message']
        self.progress_percent = data.get('progress_percent', 0.0)
        self.players_completed = data.get('players_completed', 0)
        self.points = data.get('points', 0)
        self.flags = [FortressFlag(data=flag, _client=_client) for flag in data["flags"]]


    def __repr__(self):
        return f"<Fortress '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "IP": self.ip,
            "Company": self.company.to_dict(),
            "Reset Votes": self.reset_votes,
            "Description": self.description,
            "Completion Message": self.completion_message,
            "ProgressPercent": self.progress_percent,
            "PlayersCompleted": self.players_completed,
            "Points": self.points,
            "Flags": [x.to_dict() for x in self.flags]
        }

class FortressUserProfile(BaseUserProfile):
    """Fortress user profile object. It's a kind of summary for the user profile. More details are available via the
    fortress API"""

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)

    def __repr__(self):
        return f"<FortressUserProfile '{self.name}'>"
