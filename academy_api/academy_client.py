import getpass
from typing import List
from urllib.parse import unquote

from requests import Session, codes


class AcademyClient:
    # noinspection PyUnresolvedReferences
    academy_http_request: "BaseAcademyHttpRequest"

    # noinspection PyUnresolvedReferences
    def __init__(self, academy_http_request: "BaseAcademyHttpRequest") -> None:
        assert academy_http_request is not None
        self.academy_http_request = academy_http_request
        self.academy_base_url = "https://academy.hackthebox.com"
        self.account_base_url = "https://account.hackthebox.com"

    def login(self):
        """Login to Academy and storing the session tokens"""
        sess: Session = self.academy_http_request.create_session()
        user_agent: str = self.academy_http_request.user_agent

        r = sess.get(url=f"{self.academy_base_url}/login",
                     headers={"Referer": f"{self.academy_base_url}/",
                              "User-Agent": user_agent})

        if r.status_code != codes.found:
            r = sess.get(url=f"{self.academy_base_url}/sso/redirect")
            if r.status_code != codes.ok:
                return False, f'Error during login process: {r.text} (Status code: {r.status_code})'

            username = input("Username: ")
            password = getpass.getpass("Password: ")
            r = sess.post(url=f"{self.account_base_url}/api/v1/auth/login",
                          json={"email": username, "password": password, "remember": True},
                          headers={"X-Requested-With": "XMLHttpRequest",
                                   "User-Agent": user_agent,
                                   "Accept": "application/json",
                                   "Accept-Encoding": "gzip, deflate, br",
                                   "X-Xsrf-Token": unquote(r.cookies["XSRF-TOKEN"])})

            if r.status_code != codes.ok:
                return False, f'Login failed: {r.json()["message"]}'

            two_factor_needed: bool = r.json()["two_factor"]
            if two_factor_needed:
                two_factor = input("OTP token: ")
                r = sess.post(url=f"{self.account_base_url}/api/v1/auth/two-factor-challenge",
                              json={"code": two_factor},
                              cookies=r.cookies,
                              headers={"X-Requested-With": "XMLHttpRequest",
                                       "User-Agent": user_agent,
                                       "Accept": "application/json",
                                       "Accept-Encoding": "gzip, deflate, br",
                                       "X-Xsrf-Token": unquote(r.cookies["XSRF-TOKEN"])}
                              )
                if r.status_code != codes.ok:
                    return False, f'Login failed: {r.json()["message"]}'

            intended_route = unquote(r.json()["intended_route"])
            r = sess.get(url=intended_route,
                         cookies=r.cookies,
                         headers={"Referer": f"{self.account_base_url}/login", "User-Agent": user_agent})

            cookies_dict = r.cookies.get_dict()
            res_cookies = {}
            for k, v in cookies_dict.items():
                res_cookies[unquote(k)] = unquote(v)

            return True, res_cookies

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