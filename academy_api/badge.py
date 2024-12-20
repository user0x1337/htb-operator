from typing import List, Optional

from academy_api import academy_client


class BadgeCategory(academy_client.BaseAcademyApiObject):
    title: str
    description: str
    order: int
    badges: List["Badge"]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "AcademyClient"):
        self._client = _client
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.order = data['order']
        self.badges = [Badge(data=x, _client=_client, badge_category=self) for x in data['badges']]

    def __repr__(self):
        return f'<BadgeCategory {self.id} | {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'badges': [x.to_dict() for x in self.badges]
        }


class Badge(academy_client.BaseAcademyApiObject):
    title: str
    description: str
    order: int
    logo: str
    sharing_url: str
    awarded: bool
    awarded_at: Optional[str]
    is_recently_awarded: bool
    requisites: dict[str, list]
    badge_category: BadgeCategory

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "AcademyClient", badge_category: BadgeCategory) -> None:
        self._client = _client
        self.badge_category = badge_category
        self.id = data['id']
        self.title = data['title']
        self.order = data['order']
        self.logo = data['logo']
        self.sharing_url = data['sharing_url']
        self.awarded = data['awarded']
        self.awarded_at = data.get('awarded_at')
        self.is_recently_awarded = data.get('is_recently_awarded', False)
        self.requisites = data['requisites']

    def __repr__(self):
        return f'<Badge {self.id} | {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'logo': self.logo,
            'sharing_url': self.sharing_url,
            'awarded': self.awarded,
            'awarded_at': self.awarded_at,
            'is_recently_awarded': self.is_recently_awarded,
            'requisites': self.requisites,
        }