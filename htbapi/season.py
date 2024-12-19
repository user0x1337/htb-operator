import datetime
from datetime import timezone
from typing import Optional
import dateutil.parser

from htbapi import client


class SeasonList(client.BaseHtbApiObject):
    name: str
    subtitle: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    state: str
    is_visible: bool
    active: bool

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data['id']
        self.name = data['name']
        self.subtitle = data.get('subtitle')
        self.start_date = dateutil.parser.parse(data['start_date']).replace(tzinfo=timezone.utc)
        self.end_date = None if "end_date" not in data else dateutil.parser.parse(data['end_date']).replace(tzinfo=timezone.utc)
        self.state = data['state']
        self.is_visible = data['is_visible']
        self.active = data['active']

    def __repr__(self):
        return f"<SeasonList '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subtitle": self.subtitle,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "state": self.state,
            "is_visible": self.is_visible,
            "active": self.active,
        }


class SeasonLeaderboardUserPosition(client.BaseHtbApiObject):
    rank: int
    league_rank: str
    name: str  # username
    country: str
    points: int
    user_owns: int
    root_owns: int
    user_bloods: int
    root_bloods: int
    is_respected: bool
    last_own: datetime

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data['resource_id']  # user_id
        self.name = data['name']
        self.league_rank = data['league_rank']
        self.country = data['country']
        self.points = data['points']
        self.user_owns = data['user_owns']
        self.root_owns = data['root_owns']
        self.user_bloods = data['user_bloods']
        self.root_bloods = data['root_bloods']
        self.is_respected = data['is_respected']
        self.last_own = dateutil.parser.parse(data['last_own'])

    def __repr__(self):
        return f"<SeasonLeaderboardUserPosition '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "league_rank": self.league_rank,
            "country": self.country,
            "points": self.points,
            "user_owns": self.user_owns,
            "root_owns": self.root_owns,
            "user_bloods": self.user_bloods,
            "root_bloods": self.root_bloods,
            "is_respected": self.is_respected,
            "last_own": self.last_own
        }

class SeasonUserDetails(client.BaseHtbApiObject):
    name: str
    tier: str
    season_id: int
    user_name: str
    current_rank: int
    total_ranks: int
    rank_suffix: str
    user_flags_pawned: int
    user_bloods_pawned: int
    root_flags_pawned: int
    root_bloods_pawned: int
    total_machines: int

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client

        self.id = data["user"]["id"]
        self.season_id = data["season"]['id']
        self.name = data["season"]['name']
        self.tier = data["season"]["tier"]
        self.user_name = data["user"]["name"]
        self.current_rank = data["rank"]["current"]
        self.total_ranks = data["rank"]["total"]
        self.rank_suffix = data["rank"]["suffix"]
        self.user_flags_pawned = data["owns"]["user"]["flags_pawned"]
        self.user_bloods_pawned = data["owns"]["user"]["bloods_obtained"]
        self.root_flags_pawned = data["owns"]["root"]["flags_pawned"]
        self.root_bloods_pawned = data["owns"]["root"]["bloods_obtained"]
        self.total_machines = data["owns"]["total_machines"]


    def __repr__(self):
        return f"<SeasonUserDetails '{self.name} | User: {self.id} | {self.user_name}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tier": self.tier,
            "season_id": self.season_id,
            "user_name": self.user_name,
            "current_rank": self.current_rank,
            "total_ranks": self.total_ranks,
            "rank_suffix": self.rank_suffix,
            "user_flags_pawned": self.user_flags_pawned,
            "user_bloods_pawned": self.user_bloods_pawned,
            "root_flags_pawned": self.root_flags_pawned,
            "root_bloods_pawned": self.root_bloods_pawned,
            "total_machines": self.total_machines,
        }