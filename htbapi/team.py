from typing import Optional, List

from htbapi import client, RequestException


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
    points: int
    current_bracket: str
    next_bracket: str
    # noinspection PyUnresolvedReferences
    __team_members: List["User"] = []

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)

        self.motto = data.get('motto', None)
        self.country_name = data.get('country_name', None)
        self.country_code = data.get('country_code', None)
        self.captain_user_id = data["captain"]["id"] if data is not None and len(data.keys()) > 0 and "captain" in data else None
        self.captain_username = data["captain"]["name"] if data is not None and len(data.keys()) > 0 and "captain" in data else None

        if data is not None and len(data.keys()) > 0:
            ranking_data: dict = self._client.htb_http_request.get_request(endpoint=f"rankings/team/ranking_bracket/{self.id}")
            if ranking_data is None or len(ranking_data.keys()) == 0 or "data" not in ranking_data.keys():
                ranking_data = {}
            else:
                ranking_data = ranking_data["data"]
        else:
            ranking_data = {}

        self.rank = str(ranking_data.get('rank', 0))
        self.points = ranking_data.get('points', 0)
        self.current_bracket = ranking_data.get('current_bracket', "")
        self.next_bracket = ranking_data.get('next_bracket', "")


    # noinspection PyUnresolvedReferences
    def get_team_members(self) -> List["User"]:
        """Get the list of users that are part of the team."""
        from .user import User

        if self.id < 1:
            return []

        data: list = self._client.htb_http_request.get_request(endpoint=f"team/members/{self.id}")
        if data is None or len(data) == 0:
            return []

        return [self._client.get_user(user_id=d["id"]) for d in data]

    # noinspection PyUnresolvedReferences
    def get_invitations(self) -> List["User"]:
        """Get the list of users that are invited to the team."""
        from .user import User

        try:
            data: dict = self._client.htb_http_request.get_request(endpoint=f"team/invitations/{self.id}")
            if data is None or len(data.keys()) == 0 or "original" not in data.keys():
                return []
        except RequestException:
            return []

        data = data["original"]
        return [self._client.get_user(user_id=d["user"]["id"]) for d in data]

    def __repr__(self):
        return f"<Team '{self.name} | {self.id}'>"

    def to_dict(self):
        # "Fake" / "Empty" Teams does not have any information
        if self.id < 1:
            return {
                "Id": self.id,
                "Name": self.name
            }

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
            "TeamMembers": [x.to_dict(export_team=False) for x in self.__team_members],
            "Points": self.points,
            "CurrentBracket": self.current_bracket,
            "NextBracket": self.next_bracket
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