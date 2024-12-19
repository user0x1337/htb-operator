from datetime import datetime, timezone
from typing import Optional, List

import dateutil.parser

from htbapi import client, RequestException, IncorrectArgumentException, User
from htbapi.base_user_profile import BaseUserProfile


class MachineBase(client.BaseHtbApiObject):
    name: str
    ip: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data['id']
        self.name = data['name']
        self.ip = None if 'ip' not in data else data.get('ip')

    def _execute_post_machine_call(self, endpoint: str) -> [bool, str]:
        try:
            data: dict = self._client.htb_http_request.post_request(endpoint=endpoint, json={'machine_id': self.id})
            if "success" in data and type(data["success"]) == str and data["success"] == '0':
                return False, data["message"]
            elif "success" not in data:
                return True, data["message"]
        except RequestException as e:
            return False, e.args[0]["message"]
        return data["success"], data["message"]

    def start(self) -> [bool, str]:
        return self._execute_post_machine_call(endpoint="vm/spawn")

    def stop(self) -> [bool, str]:
        return self._execute_post_machine_call(endpoint="vm/terminate")

    def reset(self) -> [bool, str]:
        return self._execute_post_machine_call(endpoint="vm/reset")

    def extend(self) -> [bool, str]:
        return self._execute_post_machine_call(endpoint="vm/extend")

    def submit(self, flag: str) -> [bool, str]:
        try:
            data: dict = self._client.htb_http_request.post_request(endpoint=f"machine/own",
                                                                    json={'machine_id': self.id, 'flag': flag},
                                                                    api_version="v5")
            return True, data["message"]
        except RequestException as e:
            return False, e.args[0]["message"]

    def rate_flag(self, difficulty: int, flag_type: str) -> [bool, str]:
        """Rate the flag given by the type parameter ("root" or "user") """
        if difficulty < 1 or difficulty > 10:
            raise IncorrectArgumentException("Difficulty must be between 1 and 10")

        try:
            data: dict = self._client.htb_http_request.post_request(endpoint=f"machine/{self.id}/flag/rate",
                                                                    json={'machine_id': self.id,
                                                                          'difficulty': difficulty,
                                                                          'type': flag_type})
            return True, data["message"]
        except RequestException as e:
            return False, e.args[0]["message"]

    def __repr__(self):
         return f"<MachineBase '{self.name} | {self.id}'>"


class MachineInfo(MachineBase):
    info_status: Optional[str]
    os: str
    active: bool
    retired: bool
    release_date: datetime
    points: int
    static_points: int
    user_owns_count: int
    root_owns_count: int
    reviews_count: int
    machine_play_info: Optional["MachinePlayInfo"]
    maker: "MachineMaker"
    recommended: bool
    sp_flag: int
    is_todo: bool
    free: bool
    authUserInUserOwns: bool
    authUserInRootOwns: bool
    authUserHasReviewed: bool
    stars: float
    difficultyText: str
    authUserFirstUserTime: Optional[str]
    authUserFirstRootTime: Optional[str]
    can_access_walkthrough: bool
    season_id: Optional[str]
    isGuidedEnabled: bool
    start_mode: Optional[str]
    show_go_vip: bool
    show_go_vip_server: bool
    ownRank: int
    machine_mode: Optional[str]
    machine_top_owns: List["MachineTopOwns"]
    machine_activity: List["MachineActivity"]
    changelog: List["MachineChangelog"]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)
        self.info_status = data.get('info_status', None)
        self.os = data.get('os', "Unknown")
        self.active = data.get('active', False)
        self.retired = data.get('retired', False)
        self.release_date = dateutil.parser.parse(data['release']).replace(tzinfo=timezone.utc)
        self.points = data.get('points', 0)
        self.static_points = data.get('static_points', 0)
        self.user_owns_count = data.get('user_owns_count', 0)
        self.root_owns_count = data.get('root_owns_count', 0)
        self.reviews_count = data.get('reviews_count', 0)
        self.machine_play_info = MachinePlayInfo(data=data["playInfo"], _client=_client, _machine_info=self) if "playInfo" in data and data["playInfo"] else None
        self.maker = MachineMaker(data=data["maker"], _client=_client, _machine_info=self) if "maker" in data else None
        self.recommended = data.get('recommended', False)
        self.sp_flag = data.get('sp_flag', 0)
        self.is_todo = data.get('isTodo', False)
        self.free = data.get('free', False)
        self.authUserInUserOwns = data.get('authUserInUserOwns', False)
        self.authUserInRootOwns = data.get('authUserInRootOwns', False)
        self.authUserHasReviewed = data.get('authUserHasReviewed', False)
        self.stars = data.get('stars', 0.0) if "stars" in data else data.get('star', 0.0) if "star" in data else 0.0
        self.difficultyText = data.get('difficultyText')
        self.authUserFirstUserTime = None if data.get('authUserFirstUserTime', None) else data.get('authUserFirstUserTime')
        self.authUserFirstRootTime = None if data.get('authUserFirstRootTime', None) else data.get('authUserFirstRootTime')
        self.can_access_walkthrough = data.get('can_access_walkthrough', False)
        self.season_id = None if data.get('season_id', None) else data.get('season_id')
        self.isGuidedEnabled = data.get('isGuidedEnabled', False)
        self.start_mode = None if data.get('start_mode', None) else data.get('start_mode')
        self.show_go_vip = data.get('show_go_vip', False)
        self.show_go_vip_server = data.get('show_go_vip_server', False)
        self.ownRank = data.get('ownRank', 0)
        self.machine_mode = None if data.get('machine_mode', None) else data.get('machine_mode')

    def __repr__(self):
         return f"<MachineInfo '{self.name} | {self.id}'>"

    def __getattr__(self, item):
        """Retrieve attributes not given

        Some endpoints only provide a subset of the attributes available for a given object.
        If these extra attributes are requested, the object will request the full data from the
        API and fill out the missing items.

        Args:
            item: The name of the property to retrieve
        """
        if item == "machine_top_owns":
            data: dict = self._client.htb_http_request.get_request(endpoint=f"machine/owns/top/{self.id}")["info"]
            new_obj = [MachineTopOwns(data=x, _client=self._client, machine_info=self) for x in data]
            new_obj.sort(key=lambda x: x.position)
        elif item == "machine_activity":
            data: dict = self._client.htb_http_request.get_request(endpoint=f"machine/activity/{self.id}")
            if "info" not in data:
                new_obj = []
            elif "activity" not in data["info"]:
                new_obj = []
            else:
                data = data["info"]["activity"]
                new_obj = [MachineActivity(data=x, _client=self._client, machine_info=self) for x in data]
                new_obj.sort(key=lambda x: x.created_at, reverse=True)
        elif item == "changelog":
            data: dict = self._client.htb_http_request.get_request(endpoint=f"machine/changelog/{self.id}")
            if "info" not in data:
                return []

            data = data["info"]
            new_obj = [MachineChangelog(data=x, _client=self._client, machine_info=self) for x in data]
            new_obj.sort(key=lambda x: x.created_at, reverse=True)
        else:
            raise AttributeError

        setattr(self, item, new_obj)
        return new_obj


    def __eq__(self, other):
        return other is not None and type(other) == type(self) and self.id == other.id

    def to_dict(self, details:bool = False):
        res = {
            "id": self.id,
            "name": self.name,
            "info_status": self.info_status,
            "os": self.os,
            "active": self.active,
            "retired": self.retired,
            "release_date": self.release_date,
            "points": self.points,
            "static_points": self.static_points,
            "user_owns_count": self.user_owns_count,
            "root_owns_count": self.root_owns_count,
            "reviews_count": self.reviews_count,
            "machine_play_info": None if self.machine_play_info is None else self.machine_play_info.to_dict(),
            "maker": None if self.maker is None else self.maker.to_dict(),
            "recommended": self.recommended,
            "sp_flag": self.sp_flag,
            "is_todo": self.is_todo,
            "ip": self.ip,
            "free": self.free,
            "authUserInUserOwns": self.authUserInUserOwns,
            "authUserInRootOwns": self.authUserInRootOwns,
            "authUserHasReviewed": self.authUserHasReviewed,
            "stars": self.stars,
            "difficultyText": self.difficultyText,
            "authUserFirstUserTime": self.authUserFirstUserTime,
            "authUserFirstRootTime": self.authUserFirstRootTime,
            "can_access_walkthrough": self.can_access_walkthrough,
            "season_id": self.season_id,
            "isGuidedEnabled": self.isGuidedEnabled,
            "start_mode": self.start_mode,
            "show_go_vip": self.show_go_vip,
            "show_go_vip_server": self.show_go_vip_server,
            "ownRank": self.ownRank,
            "machine_mode": self.machine_mode,
        }
        if details:
            res["machine_top_owns"] = [x.to_dict() for x in self.machine_top_owns]
            res["machine_activity"] = [x.to_dict() for x in self.machine_activity]
            res["changelog"] = [x.to_dict() for x in self.changelog]

        return res

class ActiveMachineInfo(MachineBase):
    name: str
    expires_at: datetime
    isSpawning: bool
    lab_server: str
    tier_id: Optional[int]
    type: str
    vpn_server_id: Optional[int]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)
        self.isSpawning = data.get('isSpawning', False)
        self.ip = 'Assigning...' if self.isSpawning else '-' if data.get('ip', '-') is None else data.get('ip')
        self.expires_at = dateutil.parser.parse(data.get('expires_at'))
        self.lab_server = data.get('lab_server')
        self.type = data.get('type')
        self.vpn_server_id = data.get('vpn_server_id')

        # Sometimes (probably only for retired/machine with related academy modules) the active machine API does not
        # contain an IP although was successfully spawned. Try to get the IP via profile API.
        if not self.isSpawning and ("ip" not in data or data['ip'] is None):
            machine_profile: MachineInfo = self._client.get_machine(self.id)
            self.ip = machine_profile.ip

    def __repr__(self):
        return f"<ActiveMachineInfo '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ip": self.ip,
            "expires_at": self.expires_at,
            "isSpawning": self.isSpawning,
            "lab_server": self.lab_server,
            "type": self.type,
            "vpn_server_id": self.vpn_server_id,
        }



class MachineOsUserProfile(BaseUserProfile):
    """Machine OS user profile"""

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        # machines data has "total machines" key instead of "total flags". To use the same interface and
        # data structure from BaseUserProfile, I have to rename it.
        data = {
            "name": data["name"],
            "completion_percentage": data["completion_percentage"],
            "owned_flags": data['owned_machines'],
            "total_flags": data['total_machines']
        }
        super().__init__(data, _client)


    def __repr__(self):
        return f"<MachineOsUserProfile '{self.name}'>"


class MachinePlayInfo(client.BaseHtbApiObject):
    machineInfo: MachineInfo
    is_spawned: bool
    is_spawning: bool
    is_active: bool
    active_player_count: int
    expires_at: Optional[datetime]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", _machine_info: MachineInfo):
        assert _machine_info is not None

        self._client = _client
        self.machineInfo = _machine_info
        self.is_spawning = data.get('isSpawning', False)
        self.is_spawned = data.get('isSpawned', False)
        self.is_active = data.get('isActive', False)
        self.active_player_count = data.get('active_player_count', 0)
        self.expires_at = None if data.get('expires_at', None) is None else dateutil.parser.parse(data.get('expires_at')).replace(tzinfo=timezone.utc)

    def __repr__(self):
        return f"<MachinePlayInfo '{self.machineInfo.name} | {self.machineInfo.id}'>"

    def to_dict(self):
        return {
            "is_spawned": self.is_spawned,
            "is_active": self.is_active,
            "active_player_count": self.active_player_count,
            "expires_at": self.expires_at,
        }


class MachineMaker(client.BaseHtbApiObject):
    name: str
    is_respected: bool
    machine_info: MachineInfo

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", _machine_info: MachineInfo):
        assert _machine_info is not None

        self._client = _client
        self.machine_info = _machine_info
        self.id = data.get('id')
        self.name = data.get('name')
        self.is_respected = data.get('isRespected', False)

    def __repr__(self):
        return f"<MachineMaker '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "is_respected": self.is_respected
        }


class MachineTopOwns(client.BaseHtbApiObject):
    username: str
    rank_id: int
    rank_text: str
    own_date: datetime
    user_own_date: datetime
    user_own_time: str
    root_own_tine: str
    is_user_blood: bool
    is_root_blood: bool
    position: int
    machine: MachineInfo
    user: User

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", machine_info: MachineInfo):
        assert machine_info is not None

        self.id = data.get('id')
        self._client = _client
        self.machine = machine_info
        self.username = data.get('name')
        self.rank_id = data.get('rank_id')
        self.rank_text = data.get('rank_text')
        self.own_date = dateutil.parser.parse(data.get('own_date')).replace(tzinfo=timezone.utc)
        self.user_own_date = dateutil.parser.parse(data.get('user_own_date')).replace(tzinfo=timezone.utc)
        self.user_own_time = data.get('user_own_time')
        self.root_own_tine = data.get('root_own_tine')
        self.is_user_blood = data.get('is_user_blood', False)
        self.is_root_blood = data.get('is_root_blood', False)
        self.position = data.get('position')

    def __repr__(self):
        return f"<MachineTopOwns '{self.username} | {self.id} | {self.machine}'>"

    def __getattr__(self, item):
        if item == 'user':
            new_obj = self._client.get_user(user_id=self.id)
        else:
            raise AttributeError

        setattr(self, item, new_obj)
        return new_obj

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "rank_id": self.rank_id,
            "rank_text": self.rank_text,
            "own_date": self.own_date,
            "user_own_date": self.user_own_date,
            "user_own_time": self.user_own_time,
            "root_own_tine": self.root_own_tine,
            "is_user_blood": self.is_user_blood,
            "is_root_blood": self.is_root_blood,
            "position": self.position
        }


class MachineActivity(client.BaseHtbApiObject):
    username: str
    type: str
    blood_type: Optional[str]
    created_at: datetime
    date: str
    date_diff: str
    machine: MachineInfo
    user: User

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", machine_info: MachineInfo):
        self._client = _client
        self.machine = machine_info
        self.id = data.get('user_id')
        self.type = data.get('type')
        self.username = data.get('user_name')
        self.blood_type = data.get('blood_type')
        self.created_at = dateutil.parser.parse(data.get('created_at')).replace(tzinfo=timezone.utc)
        self.date_diff = data.get('date_diff')
        self.date = data.get('date')

    def __repr__(self):
        return f"<MachineActivity '{self.username} | {self.id} | {self.machine}'>"

    def __getattr__(self, item):
        if item == 'user':
            new_obj = self._client.get_user(user_id=self.id)
        else:
            raise AttributeError

        setattr(self, item, new_obj)
        return new_obj

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "type": self.type,
            "blood_type": self.blood_type,
            "created_at": self.created_at,
            "date_diff": self.date_diff,
            "date": self.date
        }

class MachineChangelog(client.BaseHtbApiObject):
    user_id: int
    type: str  # 1 == "Change", 2 == "Update", 3 == "Bug"
    title: str
    description: str
    released: int
    created_at: datetime
    updated_at: datetime
    machine: MachineInfo
    user: User

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", machine_info: MachineInfo):
        self._client = _client
        self.machine = machine_info
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.title = data.get('title')
        self.description = data.get('description')
        self.released = data.get('released')
        self.created_at = dateutil.parser.parse(data.get('created_at')).replace(tzinfo=timezone.utc)
        self.updated_at = dateutil.parser.parse(data.get('updated_at')).replace(tzinfo=timezone.utc)

        raw_type = data.get('type')
        if raw_type == "1":
            self.type = "Change"
        elif raw_type == "2":
            self.type = "Update"
        elif raw_type == "3":
            self.type = "Bug"
        else:
            self.type = f'Unknown ({raw_type})'


    def __repr__(self):
        return f"<MachineChangelog '{self.title} | {self.user_id} | {self.machine}'>"

    def __getattr__(self, item):
        if item == 'user':
            new_obj = self._client.get_user(user_id=self.user_id)
        else:
            raise AttributeError

        setattr(self, item, new_obj)
        return new_obj

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user.to_dict(),
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "released": self.released,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
