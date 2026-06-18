from datetime import datetime
from typing import Optional, List, Tuple, Dict

import dateutil.parser

from htbapi import client

class Team(client.BaseHtbApiObject):
    name: str
    rank: str

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data.get('id', -1)
        self.name = data.get('name', '-')
        self.rank = data.get('ranking', '-')

    def __repr__(self):
        return f"<Team '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Rank": self.rank
        }

class University(Team):
    def __repr__(self):
        return f"<University '{self.name} | {self.id}'>"


class User(client.BaseHtbApiObject):
    name: str
    ranking: int
    points: int
    root_owns: int
    user_owns: int
    rank_name: int
    root_bloods: int
    user_bloods: int
    isDedicatedVip: bool
    isVip: bool
    rank: str
    rank_id: int
    next_rank: str
    rank_ownership: float
    country_name: str
    country_code: str
    server: str
    timezone: str
    team: Team
    respects: int
    university: University
    badges: Dict[int, datetime]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data['id']
        self.name = data['name']
        self.user_owns = data.get('user_owns', 0)
        self.root_owns = data.get('system_owns', 0)
        self.root_bloods = data.get('user_bloods', 0)
        self.user_bloods = data.get('system_bloods', 0)
        self.points = data['points']
        self.rank = data['rank']  # Personal rank, e.g. "Pro Hacker"
        self.rank_id = data['rank_id']
        self.next_rank = data.get('next_rank', "")
        self.rank_ownership = data.get('rank_ownership', 0.0)
        self.ranking = data.get('ranking', 0)  # Hall of Fame ranking
        self.rank_requirement = data.get('rank_requirement', 0)
        self.isDedicatedVip = data.get('isDedicatedVip', False)
        self.country_name = data.get('country_name', "")
        self.country_code = data.get('country_code', "")
        self.timezone = data.get('timezone', "")
        self.public = data.get('public', False)
        self.server = data.get('server', "")
        self.team = Team({}, _client) if data.get('team', None) is None else Team(data['team'], _client)
        self.respects = data.get('respects', 0)
        self.isVip = data.get('isVip', False)
        self.university = University({}, _client) if data.get('university', None) is None else University(data['university'], _client)

        data = self._client.htb_http_request.get_request(endpoint=f'user/profile/badges/{self.id}')["badges"]
        self.badges = {x["id"]: dateutil.parser.parse(x["pivot"]["created_at"] if "pivot" in x else None) for x in data}


    def __repr__(self):
        return f"<User '{self.name} | {self.id}'>"

    def to_dict(self, key_filter: list=None):
        """Returns the object as a dictionary.

        :arg key_filter: list of keys to filter on
        """
        res = {
            "ID": self.id,
            "Name": self.name,
            "Rank": self.rank,
            "Next rank": self.next_rank,
            "Ranking": self.ranking,
            "Points": self.points,
            "Country": self.country_name,
            "Timezone": self.timezone,
            "Server": self.server,
            "Team": self.team.to_dict(),
            "User Owns": self.user_owns,
            "System Owns": self.root_owns,
            "User Bloods": self.user_bloods,
            "System Bloods": self.user_bloods,
            "University": self.university.to_dict(),
            "Rank Requirement": self.rank_requirement,
            "Respects": self.respects,
            "Public": self.public,
            "Ownership": self.rank_ownership,
            "Subscription": "VIP" if self.isVip else
                            "VIP+" if self.isDedicatedVip else
                            "Normal",
            "Badges": self.badges,
        }

        if key_filter and len(key_filter) > 0:
            res = {k: res[k] for k in key_filter if k in res}

        return res
