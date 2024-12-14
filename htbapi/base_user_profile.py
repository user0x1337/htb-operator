from htbapi import client

class BaseUserProfile(client.BaseHtbApiObject):
    """Base user profile"""
    name: str
    completion_percentage: float
    owned_flags: int
    total_flags: int

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.name = data['name']
        self.completion_percentage = data['completion_percentage']
        self.owned_flags = int(data['owned_flags'])
        self.total_flags = int(data['total_flags'])

    def __repr__(self):
        return f"<SherlockUserProfile '{self.name}'>"

    def to_dict(self):
        return {
            "Name": self.name,
            "completion_percentage": self.completion_percentage,
            "owned_flags": self.owned_flags,
            "total_flags": self.total_flags
        }