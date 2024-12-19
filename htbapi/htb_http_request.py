import time
from json import JSONDecodeError
from typing import Optional, Union

import requests
from urllib3.exceptions import InsecureRequestWarning

from htbapi import RequestException

class BaseHtbHttpRequest:
    """Base class for HTTP requests."""
    _api_version: str
    _app_token: str
    _api_base: str
    _user_agent: str
    _download_cooldown: int

    def __init__(self,
                 app_token: str,
                 api_base: str,
                 user_agent: str,
                 download_cooldown: int,
                 api_version: str):
        assert app_token is not None
        assert api_base is not None
        assert user_agent is not None

        self._app_token = app_token
        self._api_base = api_base
        self._api_version = api_version
        self._user_agent = user_agent
        self._download_cooldown = download_cooldown

    def set_proxies(self, proxies: Optional[dict]) -> None:
        raise NotImplementedError()

    def set_verify_ssl(self, verify_ssl: bool) -> None:
        raise NotImplementedError()

    def post_request(self, endpoint: str, json=None, api_version: str = "v4") -> dict:
        raise NotImplementedError()

    def get_request(self, endpoint: Optional[str] = None, download=False, base: str = None, custom_url: Optional[str] = None) -> Union[list, dict, bytes]:
        raise NotImplementedError()


class HtbHtbHttpRequest(BaseHtbHttpRequest):
    """HTTP request for HTB API."""
    _proxies: Optional[dict]
    _verify_ssl: bool
    _http_headers: dict

    def __init__(self,
                 app_token: str,
                 api_base: str,
                 user_agent: str,
                 download_cooldown: int = 30,
                 api_version: str = "v4",
                 proxy: Optional[dict] = None) -> None:
        super().__init__(app_token=app_token,
                         api_base=api_base,
                         user_agent=user_agent,
                         download_cooldown=download_cooldown,
                         api_version=api_version)

        self._proxies = None
        self._verify_ssl = True
        # noinspection PyUnresolvedReferences
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        if proxy is not None:
            self.set_proxies({"http": proxy["http"] if "http" in proxy and len(proxy["http"]) > 0 else None,
                              "https": proxy["https"] if "https" in proxy and len(proxy["https"]) > 0 else None})
            self.set_verify_ssl(proxy["verify_ssl"].strip().lower() == "true" if "verify_ssl" in proxy else True)

        self._http_headers = {"Authorization": f"Bearer {self._app_token}",
                              "User-Agent": self._user_agent,
                              "Accept": "application/json"}


    def set_proxies(self, proxies: Optional[dict]) -> None:
        """Set proxies."""
        self._proxies = proxies

    def set_verify_ssl(self, verify_ssl: bool) -> None:
        """Set verify SSL."""
        self._verify_ssl = verify_ssl

    def post_request(self,endpoint: str, json=None, api_version: str = "v4") -> dict:
        """Send post request to HTB API."""
        if api_version is None:
            api_version = self._api_version


        while True:
            r = requests.post(url=f"{self._api_base}{api_version}/{endpoint}",
                              headers= self._http_headers,
                              json=json,
                              proxies=self._proxies,
                              verify=self._verify_ssl)
            # Due to rate limit
            if r.status_code == 429:
                time.sleep(1)
                continue
            else:
                break

        if r.status_code != requests.codes.ok:
            if r.status_code == requests.codes.no_content:
                return dict()

            if r.content and len(r.content) > 0:
                try:
                    raise RequestException(r.json())
                except JSONDecodeError:
                    raise RequestException(r.content)
            else:
                raise RequestException(r.status_code)

        return r.json()

    def get_request(self,
                    endpoint: Optional[str]=None,
                    download: bool = False,
                    base: Optional[str] = None,
                    custom_url: Optional[str]=None) -> Union[list, dict, bytes]:
        """Send a GET request to the API"""
        assert endpoint is not None or custom_url is not None

        if base is None:
            base = self._api_base

        while True:
            r = requests.get(url=custom_url if custom_url is not None else f"{base}{self._api_version}/{endpoint}",
                             headers= self._http_headers,
                             proxies=self._proxies,
                             verify=self._verify_ssl,
                             stream=download)
            if r.status_code == 429:
                time.sleep(1)
                continue
            else:
                break

        if r.status_code != requests.codes.ok:
            if r.content and len(r.content) > 0:
                try:
                    raise RequestException(r.json())
                except JSONDecodeError:
                    raise RequestException(r.content)
            else:
                raise RequestException(r.status_code)
        if download:
            return r.content
        else:
            return r.json()

