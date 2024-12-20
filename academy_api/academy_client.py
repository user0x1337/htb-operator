from typing import List


class AcademyClient:
    # noinspection PyUnresolvedReferences
    academy_http_request: "BaseAcademyHttpRequest"

    # noinspection PyUnresolvedReferences
    def __init__(self, academy_http_request: "BaseAcademyHttpRequest") -> None:
        assert academy_http_request is not None
        self.academy_http_request = academy_http_request

    def login(self):
        pass

    # noinspection PyUnresolvedReferences
    def get_skill_paths(self) -> List["SkillPath"]:
        """Get all skill paths"""
        from academy_api import SkillPath

        data = self.academy_http_request.get_request(endpoint="paths")["data"]
        if data is None:
            return []

        return [SkillPath(data=x, _client=self) for x in data]

    # noinspection PyUnresolvedReferences
    def get_badges(self) -> List["BadgeCategory"]:
        """Get all badges"""
        from academy_api import BadgeCategory

        data = self.academy_http_request.get_request(endpoint="badges")["data"]
        if data is None:
            return []

        return [BadgeCategory(_client=self, data=x) for x in data]



class BaseAcademyApiObject(object):
    _client: AcademyClient
    id: int

    def __eq__(self, other):
        return self.id == other.id and type(self) == type(other)