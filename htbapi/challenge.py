import hashlib
import os
from datetime import datetime
from typing import List, Optional, cast

import dateutil.parser

from htbapi import client, IncorrectArgumentException, User
from htbapi.base_user_profile import BaseUserProfile
from htbapi.exception.errors import IncorrectFlagException, UnknownDirectoryException, RequestException


class ChallengeBase(client.BaseHtbApiObject):
    name: str
    retired: bool
    difficulty: str
    difficulty_num: int
    points: int
    solves: int
    likes: int
    dislikes: int
    release_date: datetime
    solved: bool
    isTodo: bool
    recommended: int

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data['id']
        self.name = data.get('name', '')
        self.retired = data.get('retired', True)
        self.difficulty = data.get('difficulty', "")
        self.points = data.get('points', 0)
        self.solves = data.get('solves', 0)
        self.likes = data.get('likes', 0)
        self.dislikes = data.get('dislikes', 0)
        self.release_date =  dateutil.parser.parse(data["release_date"])
        self.solved = data.get('authUserSolve', False)
        self.isTodo = data.get('isTodo', False)
        self.recommended = data.get('recommended', 0)

        if self.difficulty.lower() == "very easy":
            self.difficulty_num = 0
        elif self.difficulty.lower() == "easy":
            self.difficulty_num = 1
        elif self.difficulty.lower() == "medium":
            self.difficulty_num = 2
        elif self.difficulty.lower() == "hard":
            self.difficulty_num = 3
        elif self.difficulty.lower() == "insane":
            self.difficulty_num = 4
        else:
            self.difficulty_num = -1


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'retired': self.retired,
            'difficulty': self.difficulty,
            'points': self.points,
            'solves': self.solves,
            'likes': self.likes,
            'dislikes': self.dislikes,
            'release_date': self.release_date,
            'solved': self.solved,
            'isTodo': self.isTodo,
            'recommended': self.recommended,
            'difficulty_num': self.difficulty_num,
            }

    def submit(self, flag: str, difficulty: int):
        if difficulty < 1 or difficulty > 10:
            raise IncorrectArgumentException("Difficulty must be between 1 and 10")

        res = self._client.htb_http_request.post_request(endpoint=f"challenge/own", json={
            "flag": flag,
            "challenge_id": self.id,
            "difficulty": difficulty*10
        })

        return res["message"] != "Incorrect flag"


    def start_instance(self) -> str:
        """Start the instance.

        :returns: The message from the backend.
        """
        data: dict = self._client.htb_http_request.post_request(endpoint=f"challenge/start", json={'challenge_id': self.id})
        return data["message"]

    def stop_instance(self) -> str:
        """Stop the instance.

        :returns: The message from the backend.
        """
        data: dict = self._client.htb_http_request.post_request(endpoint=f"challenge/stop", json={'challenge_id': self.id})
        return data["message"]


    def download(self, path: Optional[str] = None) -> str:
        if path is None:
            path = os.path.join(os.getcwd(), f'{self.name.strip().replace(" ", "_")}.zip')
        else:
            path = path.strip() + ("" if path.endswith(os.path.sep) else os.path.sep)
            path = os.path.dirname(path)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, f'{self.name.strip().replace(" ", "_")}.zip')

        try:
            data = cast(bytes, self._client.htb_http_request.get_request(endpoint=f"challenge/download/{self.id}", download=True))
        except RequestException as e:
            if not e.args or len(e.args) == 0 or "message" not in e.args[0].keys():
                raise RequestException(f"Could not download file for challenge {self.name}")
            msg = e.args[0]["message"]
            if "unauthorized" in msg:
                raise RequestException(f"Could not download file for challenge {self.name}: You are not authorized.")
            elif "Not Found" in msg:
                raise RequestException(f"Could not download file for challenge {self.name}: Certificate not found.")
            else:
                raise e
        with open(path, "wb") as f:
            f.write(data)

        return path


    def download_writeup(self, path: Optional[str] = None) -> str:
        """Download writeup"""
        data:dict = self._client.htb_http_request.get_request(endpoint=f"challenge/{self.id}/writeup")["data"]
        if "official" not in data:
            raise RequestException(f"Could not download writeup for challenge {self.name}")

        data = data["official"]
        url = data["url"]
        filename = data["filename"]
        sha256 = data["sha256"]

        if path is None:
            path = os.path.join(os.getcwd(), f'{filename}')
        else:
            path = path.strip() + ("" if path.endswith(os.path.sep) else os.path.sep)
            path = os.path.dirname(path)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, f'{filename}')

        try:
            file_data = cast(bytes, self._client.htb_http_request.get_request(custom_url=f"{url}", download=True))
        except RequestException as e:
            msg = e.args[0]["message"]
            if "unauthorized" in msg:
                raise RequestException(f"Could not download writeup for challenge {self.name}: You are not authorized.")
            elif "Not Found" in msg:
                raise RequestException(f"Could not download writeup for challenge {self.name}: Certificate not found.")
            else:
                raise e

        file_hash = hashlib.sha256(file_data).hexdigest()
        if file_hash != sha256:
            raise RequestException(f"Could not download writeup for challenge {self.name}: Hash mismatch.")

        with open(path, "wb") as f:
            f.write(file_data)

        return path


    def __repr__(self):
        return f"<Challenge '{self.name} | {self.id}'>"


class ChallengeList(ChallengeBase):
    category_id: int
    rating: float
    avg_difficulty: int
    isActive: bool # Is the instance running if the challenge has an instance?

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)
        self.category_id = int(data.get("challenge_category_id", -1))
        self.rating = data.get('rating', 0.0)
        self.avg_difficulty = data.get('avg_difficulty', 0)
        self.isActive = data.get('isActive', False)

    def to_dict(self):
        d = super().to_dict()
        d["category_id"] = self.category_id
        d["rating"] = self.rating
        d["avg_difficulty"] = self.avg_difficulty
        d["isActive"] = self.isActive
        return d

class ChallengeInfo(ChallengeBase):
    authUserSolveTime: str
    description: str
    category_name: str
    first_blood_user_id: int
    first_blood_user: str
    first_blood_time: str
    creator_id: int
    creator_name: str
    creator2_id: Optional[int]
    creator2_name: Optional[str]
    downloadable: bool
    download_sha256: str
    docker: bool
    docker_ip: Optional[str]
    docker_ports: Optional[List[int]]
    released: int
    hasReviewed: bool
    canReview: bool
    writeup_provided: bool


    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)
        self.authUserSolveTime = data.get("authUserSolveTime")
        self.description = data.get("description")
        self.category_name = data.get("category_name")
        self.first_blood_user_id = data.get("first_blood_user_id", -1)
        self.first_blood_user = data.get("first_blood_user", "")
        self.first_blood_time = data.get("first_blood_time", "")
        self.creator_id = data.get("creator_id", -1)
        self.creator_name = data.get("creator_name", "")
        self.creator2_id = data.get("creator2_id", None)
        self.creator2_name = data.get("creator2_name", None)
        self.downloadable = data.get("download", False)
        self.download_sha256 = data.get("sha256", "")
        self.docker = False if data.get("docker", False) is None else data.get("docker", False)
        self.docker_ip = data.get("docker_ip", None)
        self.docker_ports = data.get("docker_ports", None)
        self.released = data.get("released", False)
        self.hasReviewed = data.get("authUserHasReviewed", False)
        self.canReview = data.get("user_can_review", False)
        self.writeup_provided = data.get("can_access_walkthough", False) if "can_access_walkthough" in data else data.get("can_access_walkthough", False)

    @property
    def authors(self) -> List[User]:

        author1: User = self._client.get_user(user_id=self.creator_id)
        if self.creator2_id is not None:
            author2 = self._client.get_user(user_id=self.creator2_id)
            return [author1, author2]

        return [author1]

    def to_dict(self):
        d = super().to_dict()
        d["authUserSolveTime"] = self.authUserSolveTime
        d["description"] = self.description
        d["category_name"] = self.category_name
        d["first_blood_user_id"] = self.first_blood_user_id
        d["first_blood_user"] = self.first_blood_user
        d["first_blood_time"] = self.first_blood_time
        d["creator_id"] = self.creator_id
        d["creator_name"] = self.creator_name
        d["creator2_id"] = self.creator2_id
        d["creator2_name"] = self.creator2_name
        d["download"] = self.downloadable
        d["download_sha256"] = self.download_sha256
        d["docker"] = self.docker
        d["docker_ip"] = self.docker_ip
        d["docker_ports"] = self.docker_ports
        d["released"] = self.released
        d["hasReviewed"] = self.hasReviewed
        d["canReview"] = self.canReview
        d["writeup_provided"] = self.writeup_provided
        return d


class ChallengeUserProfile(BaseUserProfile):
    """Challenge user profile"""
    avg_user_solved: float

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(data, _client)
        self.avg_user_solved = data['avg_user_solved']

    def __repr__(self):
        return f"<ChallengeUserProfile '{self.name}'>"

    def to_dict(self):
        d = super().to_dict()
        d['avg_user_solved'] = self.avg_user_solved

        return d

class Category(client.BaseHtbApiObject):
    name: str
    icon_url: str

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self.id = int(data['id'])
        self.name = data['name']
        self.icon_url = data['icon']

    def __repr__(self):
        return f"<Category '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "icon_url": self.icon_url
        }