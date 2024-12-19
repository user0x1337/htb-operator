from datetime import datetime
from typing import Optional, List

import dateutil.parser

from htbapi import client, User, RequestException


class ProLabFlag(client.BaseHtbApiObject):
    """ProLab flag"""
    _pro_lab: "ProLabInfo"
    title: str
    points: int
    owned: bool

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", _pro_lab: "ProLabInfo"):
        self._pro_lab = _pro_lab
        self._client = _client
        self.id = data['id']
        self.title = data['title']
        self.points = data['points']
        self.owned = data['owned']

    def __repr__(self):
        return f"<ProLabFlag '{self.id} | {self.title}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "points": self.points,
            "owned": self.owned,
        }

class ProLabMachine(client.BaseHtbApiObject):
    """ProLab Machine"""
    _pro_lab: "ProLabInfo"
    name: str
    os: str

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", _pro_lab: "ProLabInfo"):
        self._pro_lab = _pro_lab
        self._client = _client
        self.id = data['id']
        self.name = data['name']
        self.os = data['os']

    def __repr__(self):
        return f"<ProLabMachine '{self.id} | {self.name}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "os": self.os
        }

class ProLabMilestone(client.BaseHtbApiObject):
    """ProLab milestone"""
    _pro_lab_progress: "ProLabProgres"
    percent: int
    icon: str
    text: str
    description: str
    is_milestone_reached: bool
    rarity: int

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", _pro_lab_progress: "ProLabProgres"):
        assert _pro_lab_progress is not None

        self._pro_lab_progress = _pro_lab_progress
        self._client = _client
        self.percent = data['percent']
        self.icon = data['icon']
        self.text = data['text']
        self.description = data['description']
        self.is_milestone_reached = data['is_milestone_reached']
        self.rarity = data['rarity']

    def __repr__(self):
        return f"<ProLabMilestone '{self.text}'>"

    def to_dict(self):
        return {
            "percent": self.percent,
            "icon": self.icon,
            "text": self.text,
            "description": self.description,
            "is_milestone_reached": self.is_milestone_reached,
            "rarity": self.rarity
        }


class ProLabChangeLog(client.BaseHtbApiObject):
    """ProLab Change Log"""
    _pro_lab: "ProLabInfo"
    user_id: int
    type: str
    title: str
    description: str
    created_at: datetime
    user: User

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", _pro_lab: "ProLabInfo"):
        assert _pro_lab is not None
        self.id = data['id']
        self._pro_lab = _pro_lab
        self._client = _client
        self.user_id = data['user_id']
        self.type = data['type']
        self.title = data['title']
        self.description = data['description']
        self.created_at = dateutil.parser.parse(data['created_at'])
        self.user = self._client.get_user(user_id=self.user_id)

    def __repr__(self):
        return f"<ProLabChangeLog '{self.id} | {self.title}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "type": self.type,
            "user": self.user.to_dict(),
        }

class ProLabProgres:
    """ProLab Progres"""
    _pro_lab: "ProLabInfo"
    ownership: float
    ownership_required_for_certification: int
    milestones: List[ProLabMilestone]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", _pro_lab: "ProLabInfo"):
        assert _pro_lab is not None

        self._pro_lab = _pro_lab
        self._client = _client
        self.ownership = data.get('ownership', 0.0)
        self.ownership_required_for_certification = data.get('ownership_required_for_certification', 0)
        self.milestones = [ProLabMilestone(_client=_client, data=x, _pro_lab_progress=self) for x in data.get('keyed_pro_lab_mile_stone', [])]

    def __repr__(self):
        return f"<ProLabProgres '{self.ownership}'>"

    def to_dict(self):
        return {
            "ownership": self.ownership,
            "ownership_required_for_certification": self.ownership_required_for_certification,
            "milestones": [x.to_dict() for x in self.milestones]
        }


class ProLabUserProfile(client.BaseHtbApiObject):
    """ProLab user profile"""
    name: str
    completion_percentage: float
    owned_flags: int
    total_flags: int
    total_machines: int
    average_ratings: float

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.name = data['name']
        self.completion_percentage = data['completion_percentage']
        self.owned_flags = int(data['owned_flags'])
        self.total_flags = int(data['total_flags'])
        self.total_machines = int(data['total_machines'])
        self.average_ratings = data['average_ratings']

    def __repr__(self):
        return f"<ProLabUserProfile '{self.name}'>"

    def to_dict(self):
        return {
            "Name": self.name,
            "completion_percentage": self.completion_percentage,
            "owned_flags": self.owned_flags,
            "total_flags": self.total_flags,
            "total_machines": self.total_machines,
            "average_ratings": self.average_ratings
        }


class ProLabInfo(client.BaseHtbApiObject):
    """ProLab info"""
    name: str
    release_date: datetime
    machines_count: int
    flags_count: int
    state: Optional[str]
    mini: bool
    identifier: str
    ownership: float # in percent
    user_eligible_for_certificate: bool
    new: bool
    skill_level: str
    designated_category: str
    team: str
    level: int
    lab_servers_count: int

    # Detail information
    version: str
    entry_points: list[str]
    description: str
    active_users: int
    lab_masters: List["ProLabMasterInfo"]
    writeup_filename: Optional[str]
    writeup_link: Optional[str]

    # Detail "overview" information
    discord_url: Optional[str] = None

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data['id']
        self.name = data['name']
        self.release_date = dateutil.parser.parse(data['release_at'])
        self.machines_count = int(data.get('pro_machines_count', 0))
        self.flags_count = int(data.get('pro_flags_count', 0))
        self.state = data.get('state', None)
        self.mini = data.get('mini', False)
        self.identifier = data.get('identifier')
        self.ownership = data.get('ownership')
        self.user_eligible_for_certificate = data.get('user_eligible_for_certificate', False)
        self.new = data.get('new', False)
        self.skill_level = data.get('skill_level')
        self.designated_category = data.get('designated_category')
        self.team = data.get('team')
        self.level = data.get('level', 0)
        self.lab_servers_count = data.get('lab_servers_count', 0)

        detail_data:dict = self._client.htb_http_request.get_request(endpoint=f"prolab/{self.id}/info")["data"]
        if detail_data is not None:
            self.version = detail_data.get('version')
            self.description = detail_data.get('description')
            self.entry_points = detail_data.get('entry_points')
            self.active_users = detail_data.get('active_users')
            self.lab_masters = [ProLabMasterInfo(data=x, _client=_client) for x in detail_data.get("lab_masters")]
            self.writeup_filename = None if detail_data.get('writeup') is None else detail_data["writeup"]["file_name"]
            self.writeup_link = None if detail_data.get('writeup') is None else detail_data["writeup"]["link"]

        overview_data: dict = self._client.htb_http_request.get_request(endpoint=f"prolab/{self.id}/overview")["data"]
        if overview_data is not None:
            self.discord_url = overview_data["social_links"].get('discord', None) if "social_links" in overview_data else None
            self.forum = overview_data["social_links"].get('forum', None) if "social_links" in overview_data else None


    def get_flags(self) -> [ProLabFlag]:
        """Get the corresponding flags"""
        res: dict = self._client.htb_http_request.get_request(endpoint=f"prolab/{self.id}/flags")
        if "status" in res and res["status"]:
            return sorted([ProLabFlag(_client=self._client, data=x, _pro_lab=self) for x in res["data"]], key=lambda flag: flag.id)
        else:
            return []

    def get_machines(self) -> List[ProLabMachine]:
        """Get the corresponding machines"""
        res: dict = self._client.htb_http_request.get_request(endpoint=f"prolab/{self.id}/machines")
        if "status" in res and res["status"]:
            return sorted([ProLabMachine(_client=self._client, data=x, _pro_lab=self) for x in res["data"]], key=lambda flag: flag.id)
        else:
            return []

    def get_progress(self) -> Optional[ProLabProgres]:
        """Get the progress"""
        res: dict = self._client.htb_http_request.get_request(endpoint=f"prolab/{self.id}/progress")
        if "status" in res and res["status"]:
            return ProLabProgres(_client=self._client, data=res["data"], _pro_lab=self)
        else:
            return None

    def get_changelogs(self) -> List[ProLabChangeLog]:
        """Get changelogs"""
        res: dict = self._client.htb_http_request.get_request(endpoint=f"prolab/{self.id}/changelogs")
        if "status" in res and res["status"]:
            return [ProLabChangeLog(_client=self._client, data=x, _pro_lab=self) for x in res["data"]]
        else:
            return []

    def submit_flag(self, flag: str) -> [bool, str]:
        """Submit a flag"""
        try:
            data: dict = self._client.htb_http_request.post_request(endpoint=f"prolab/{self.id}/flag", json={'flag': flag})
            return True, data["message"]
        except RequestException as e:
            return False, e.args[0]["message"]

    def get_reset_status(self) -> [Optional[str], Optional[datetime]]:
        """Get the progress. Returns a datetime if successful (and string is None), otherwise a string and datetime is None."""
        try:
            res: dict = self._client.htb_http_request.get_request(endpoint=f"prolab/{self.id}/reset")
            if "status" in res and res["status"] == "online":
                return None, dateutil.parser.parse(res["data"]["last_reverted"])
            else:
                return res["message"], None
        except RequestException as e:
            return e.args[0]["message"], None


    def __repr__(self):
        return f"<ProLabInfo '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "release_date": self.release_date,
            "machines_count": self.machines_count,
            "flags_count": self.flags_count,
            "state": self.state,
            "mini": self.mini,
            "identifier": self.identifier,
            "ownership": self.ownership,
            "discord_url": self.discord_url,
            "forum": self.forum,
            "user_eligible_for_certificate": self.user_eligible_for_certificate,
            "new": self.new,
            "skill_level": self.skill_level,
            "designated_category": self.designated_category,
            "team": self.team,
            "level": self.level,
            "lab_servers_count": self.lab_servers_count,
            "version": self.version,
            "entry_points": self.entry_points,
            "description": self.description,
            "active_users": self.active_users,
            "lab_masters": [x.to_dict() for x in self.lab_masters],
            "flags": [x.to_dict() for x in self.get_flags()],
            "machines": [x.to_dict() for x in self.get_machines()],
            "writeup_filename": self.writeup_filename,
            "writeup_link": self.writeup_link
        }


class ProLabMasterInfo(client.BaseHtbApiObject):
    name: str
    user_id: int

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data['id']
        self.name = data['name']
        self.user_id = self.id

    def __repr__(self):
        return f"<ProLabMasterInfo '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
        }