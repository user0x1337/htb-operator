from datetime import datetime
from typing import Optional

import dateutil.parser

from htbapi import client


class Activity(client.BaseHtbApiObject):
    name: str
    points: int
    date: datetime
    date_diff: str
    object_type: str
    first_blood: bool
    type: str    # challenge, user, root, endgame
    challenge_category: Optional[str]    # Optional, only for challenges
    url_machine_avatar: Optional[str]    # Optional, only for machines
    flag_title: Optional[str]          # Optional, only for endgabe

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data.get('id', -1)
        self.name = data.get('name', '-')
        self.points = data.get('points', 0)
        self.date = dateutil.parser.parse(data.get('date'))
        self.date_diff = data.get('date_diff')
        self.object_type = data.get('object_type')
        self.type = data.get('type')
        self.first_blood = data.get('firstBlood', False)
        self.challenge_category = data.get('challenge_category', None)
        self.url_machine_avatar = data.get('machine_avatar', None)
        self.flag_title = data.get('flag_title', None)

    def __repr__(self):
        return f"<Activity '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Points": self.points,
            "Date": self.date.isoformat(),
            "DateDiff": self.date_diff,
            "ObjectType": self.object_type,
            "Type": self.type,
            "firstBlood": self.first_blood,
            "ChallengeCategory": self.challenge_category,
            "URLMachineAvatar": self.url_machine_avatar,
            "FlagTitle": self.flag_title
        }