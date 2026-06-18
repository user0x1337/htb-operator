import time
from json import JSONDecodeError
from typing import Optional, Union

import httpx

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

    def get_request(self, endpoint: Optional[str] = None, download=False, base: str = None, custom_url: Optional[str] = None, api_version: Optional[str] = None) -> Union[list, dict, bytes]:
        raise NotImplementedError()


class HtbHtbHttpRequest(BaseHtbHttpRequest):
    """HTTP request for HTB API."""
    _proxies: Optional[dict]
    _verify_ssl: bool
    _http_headers: dict
    _client: httpx.Client

    def __init__(self,
                 app_token: str,
                 api_base: str,
                 user_agent: str,
                 download_cooldown: int = 30,
                 api_version: str = "v4",
                 proxy: Optional[dict] = None,
                 verify_ssl: bool = True) -> None:
        super().__init__(app_token=app_token,
                         api_base=api_base,
                         user_agent=user_agent,
                         download_cooldown=download_cooldown,
                         api_version=api_version)

        self._proxies = None
        self._verify_ssl = True
        self.set_verify_ssl(verify_ssl)
        if proxy is not None and ("http" in proxy or "https" in proxy):
            self.set_proxies({"http": proxy["http"] if "http" in proxy and len(proxy["http"]) > 0 else None,
                              "https": proxy["https"] if "https" in proxy and len(proxy["https"]) > 0 else None})

        self._http_headers = {"Authorization": f"Bearer {self._app_token}",
                              "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
                              "Accept": "application/json",
                              "Referer": "https://app.hackthebox.com/",
                              "Origin": "https://app.hackthebox.com",}

        # build HTTP/2 client
        self._client = self._build_client()

    def _build_client(self) -> httpx.Client:
        """Create a configured HTTP/2 client."""
        transport = None
        if self._proxies:
            proxy_url = self._proxies.get("https") or self._proxies.get("http")
            if proxy_url:
                transport = httpx.HTTPTransport(proxy=proxy_url)

        # modern signature
        if transport is not None:
            return httpx.Client(http2=True,
                                headers=self._http_headers,
                                verify=self._verify_ssl,
                                follow_redirects=True,
                                max_redirects=2,
                                transport=transport)
        else:
            return httpx.Client(http2=True,
                                headers=self._http_headers,
                                verify=self._verify_ssl,
                                follow_redirects=True,
                                max_redirects=2)



    def set_proxies(self, proxies: Optional[dict]) -> None:
        """Set proxies."""
        self._proxies = proxies
        # Recreate client to apply new proxies
        self._client = self._build_client()

    def set_verify_ssl(self, verify_ssl: bool) -> None:
        """Set verify SSL."""
        self._verify_ssl = verify_ssl
        # Recreate client to apply new SSL setting
        # (client may not yet exist during __init__, so guard it)
        try:
            self._client = self._build_client()
        except AttributeError:
            pass

    def post_request(self,endpoint: str, json=None, api_version: str = "v4") -> dict:
        """Send post request to HTB API."""
        if api_version is None:
            api_version = self._api_version


        while True:
            r = self._client.post(url=f"{self._api_base}{api_version}/{endpoint}",
                                  json=json)
            # Due to rate limit
            if r.status_code == 429:
                time.sleep(1)
                continue
            else:
                break

        if r.status_code != httpx.codes.OK:
            if r.status_code == httpx.codes.NO_CONTENT:
                return dict()

            if r.content and len(r.content) > 0:
                try:
                    raise RequestException(r.json())
                except JSONDecodeError:
                    # ensure callers expecting a mapping don't break on bytes
                    text = r.content.decode('utf-8', errors='replace')
                    raise RequestException({"message": text, "status_code": r.status_code})
            else:
                raise RequestException(r.status_code)

        return r.json()

    def get_request(self,
                    endpoint: Optional[str]=None,
                    download: bool = False,
                    base: Optional[str] = None,
                    custom_url: Optional[str]=None,
                    api_version: Optional[str] = None) -> Union[list, dict, bytes]:
        """Send a GET request to the API"""
        assert endpoint is not None or custom_url is not None

        if api_version is None:
            api_version = self._api_version

        if base is None:
            base = self._api_base

        url = custom_url if custom_url is not None else f"{base}{api_version}/{endpoint}"

        # Stream downloads in chunks to reduce memory usage and support large files
        if download:
            while True:
                with self._client.stream("GET", url) as r:
                    if r.status_code == 429:
                        # rate limited, retry after short sleep
                        time.sleep(1)
                        continue

                    if r.status_code != httpx.codes.OK:
                        # read body to include details in exception
                        body = r.read()
                        if body:
                            try:
                                raise RequestException(r.json())
                            except JSONDecodeError:
                                # normalize to a dict so upstream code using .keys() won't fail
                                text = body.decode('utf-8', errors='replace')
                                raise RequestException({"message": text, "status_code": r.status_code})
                        else:
                            raise RequestException(r.status_code)

                    # status OK: collect bytes in chunks
                    buf = bytearray()
                    for chunk in r.iter_bytes():  # default reasonable chunk size
                        if chunk:
                            buf.extend(chunk)
                    return bytes(buf)
        else:
            while True:
                r = self._client.get(url=url)
                if r.status_code == 429:
                    time.sleep(1)
                    continue
                else:
                    break

            if r.status_code != httpx.codes.OK:
                if r.content and len(r.content) > 0:
                    try:
                        raise RequestException(r.json())
                    except JSONDecodeError:
                        text = r.content.decode('utf-8', errors='replace')
                        raise RequestException({"message": text, "status_code": r.status_code})
                else:
                    raise RequestException(r.status_code)

            return r.json()

