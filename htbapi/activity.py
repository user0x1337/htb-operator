from datetime import datetime
from typing import Optional

import dateutil.parser
from dateutil.relativedelta import relativedelta

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
        self.date = dateutil.parser.parse(data.get('ownDate'))
        self.date_diff = self._human_date_diff()
        self.object_type = data.get('categoryName')
        self.type = data.get('type')
        self.first_blood = data.get('blood', False)
        self.challenge_category = data.get('challenge_category', None)
        self.url_machine_avatar = data.get('avatar', None)
        self.flag_title = None

    def _human_date_diff(self) -> str:
        """
        Returns strings like:
        - 3 years ago
        - 1 month ago
        - 4 days ago
        - 2 hours ago
        - 4 seconds ago
        """

        if self.date.tzinfo is not None:
            now = datetime.now(self.date.tzinfo)
        else:
            now = datetime.now()

        future = self.date > now

        start = now if future else self.date
        end = self.date if future else now

        diff = relativedelta(end, start)

        units = [
            ("year", diff.years),
            ("month", diff.months),
            ("day", diff.days),
            ("hour", diff.hours),
            ("minute", diff.minutes),
            ("second", diff.seconds),
        ]

        for unit, value in units:
            if value:
                suffix = "" if value == 1 else "s"
                if future:
                    return f"in {value} {unit}{suffix}"
                return f"{value} {unit}{suffix} ago"

        return "just now"

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