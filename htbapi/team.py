from typing import Optional, List

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
    __team_members: List["User"] = []

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)

        self.motto = data.get('motto', None)
        self.country_name = data.get('country_name', None)
        self.country_code = data.get('country_code', None)
        self.captain_user_id = data["captain"]["id"] if "captain" in data else None
        self.captain_username = data["captain"]["name"]


    # noinspection PyUnresolvedReferences
    def get_team_members(self) -> List["User"]:
        """Get the list of users that are part of the team."""
        from .user import User
        data: list = self._client.htb_http_request.get_request(endpoint=f"team/members/{self.id}")
        if data is None or len(data) == 0:
            return []

        return [self._client.get_user(user_id=d["id"]) for d in data]

    def __repr__(self):
        return f"<Team '{self.name} | {self.id}'>"

    def to_dict(self):
        if len(self.__team_members) == 0:
            self.__team_members = self.get_team_members()

        return {
            "Id": self.id,
            "Name": self.name,
            "Rank": self.rank,
            "Motto": self.motto,
            "CountryName": self.country_name,
            "CountryCode": self.country_code,
            "CaptainUserID": self.captain_user_id,
            "CaptainUsername": self.captain_username,
            "TeamMembers": [x.to_dict(export_team=False) for x in self.__team_members]
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