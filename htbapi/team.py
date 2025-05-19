from typing import Optional

from htbapi import client

class Base(client.BaseHtbApiObject):
    name: str
    rank: str

    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data.get('id', -1)
        self.name = data.get('name', '-')
        self.rank = data.get('ranking', '-')


class Team(Base):
    motto: Optional[str]
    country_name: Optional[str]
    country_code: Optional[str]
    captain_user_id: Optional[int]
    captain_username: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)

        self.motto = data.get('motto', None)
        self.country_name = data.get('country_name', None)
        self.country_code = data.get('country_code', None)
        self.captain_user_id = data["captain"]["id"] if "captain" in data else None
        self.captain_username = data["captain"]["name"]


    def __repr__(self):
        return f"<Team '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Rank": self.rank
        }

class University(Base):
    def __repr__(self):
        return f"<University '{self.name} | {self.id}'>"

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)

    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Rank": self.rank
        }