from datetime import datetime, timezone
from typing import Optional

import dateutil.parser

from htbapi import client, RequestException
from htbapi.base_user_profile import BaseUserProfile


class SherlockUserProfile(BaseUserProfile):
    """Sherlock user profile"""
    avg_user_solved: float

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)
        self.avg_user_solved = data['avg_user_solved']

    def __repr__(self):
        return f"<SherlockUserProfile '{self.name}'>"

    def to_dict(self):
        d = super().to_dict()
        d['avg_user_solved'] = self.avg_user_solved

        return d


class SherlockInfo(client.BaseHtbApiObject):
    """Sherlock info"""
    name: str
    difficulty: str
    state: str
    category_id: int
    category_name: str
    solves: int
    is_owned: bool
    rating: float
    rating_count: int
    auth_user_has_reviewed: bool
    progress: float
    release_date: datetime
    pinned: bool

    # Detailed Information
    writeup_visible: Optional[bool]
    retired: Optional[bool]
    show_go_vip: Optional[bool]
    isTodo: Optional[bool]
    favorite: Optional[bool]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", get_details: bool = False):
        self._client = _client
        self.id = data['id']
        self.name = data['name']
        self.difficulty = data['difficulty']
        self.state = data['state']
        self.category_id = data['category_id']
        self.category_name = data['category_name']
        self.solves = data['solves']
        self.is_owned = data['is_owned']
        self.rating = data['rating']
        self.rating_count = data['rating_count']
        self.auth_user_has_reviewed = data['auth_user_has_reviewed']
        self.progress = data['progress']
        self.release_date = dateutil.parser.parse(data['release_date']).replace(tzinfo=timezone.utc)
        self.pinned = data['pinned']

        if get_details:
            details_data = self._client.htb_http_request.get_request(endpoint=f"sherlocks/{self.id}")
            if details_data and "data" in details_data:
                details_data: dict = details_data["data"]
                self.writeup_visible = details_data['writeup_visible']
                self.retired = details_data['retired']
                self.show_go_vip = details_data['show_go_vip']
                self.isTodo = details_data["isTodo"]
                self.favorite = details_data['favorite']
        else:
            self.writeup_visible = None
            self.show_go_vip = None
            self.retired = None
            self.favorite = None
            self.isTodo = None

    def get_writeup(self) -> Optional["SherlockWriteup"]:
        try:
            data: dict = self._client.htb_http_request.get_request(endpoint=f"sherlocks/{self.id}/writeup")
        except RequestException as e:
            return None

        if "data" in data:
            data = data["data"]
            return SherlockWriteup(_client=self._client, data=data["official"], sherlock_parent=self)
        else:
            return None

    def __repr__(self):
        return f"<SherlockInfo '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "difficulty": self.difficulty,
            "state": self.state,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "solves": self.solves,
            "is_owned": self.is_owned,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "auth_user_has_reviewed": self.auth_user_has_reviewed,
            "progress": self.progress,
            "release_date": self.release_date,
            "pinned": self.pinned,
            "writeup_visible": self.writeup_visible,
            "retired": self.retired,
            "show_go_vip": self.show_go_vip,
            "favorite": self.favorite,
        }

class SherlockWriteup(client.BaseHtbApiObject):
    """Sherlock writeup"""
    _sherlock_parent: SherlockInfo
    filename: Optional[str]
    sha256: Optional[str]
    url: Optional[str]
    video_url: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient", sherlock_parent: SherlockInfo):
        self._client = _client
        self._sherlock_parent = sherlock_parent
        self.filename = data.get('filename')
        self.sha256 = data.get('sha256')
        self.url = data.get('url')
        self.video_url = data.get('video_url')

    def __repr__(self):
        return f"<SherlockWriteup '{self.filename} | {self._sherlock_parent}'>"

    def to_dict(self):
        return {
            "filename": self.filename,
            "sha256": self.sha256,
            "url": self.url,
            "video_url": self.video_url,
        }

class SherlockCategory(client.BaseHtbApiObject):
    """Sherlock category"""
    name: str

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data.get('id')
        self.name = data.get('name')

    def __repr__(self):
        return f"<SherlockCategory '{self.id} | {self.name}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }