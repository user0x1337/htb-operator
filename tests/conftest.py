from __future__ import annotations

from typing import Any, Dict, List, Tuple

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import htbapi.client as client_mod
from htbapi import HTBClient


class StubHtbHttpRequest:
    """Simple stub for BaseHtbHttpRequest that never performs real HTTP calls."""

    def __init__(self) -> None:
        self.get_routes: Dict[str, List[Any]] = {}
        self.post_routes: Dict[str, List[Any]] = {}
        self.calls: List[Tuple[str, str, Dict[str, Any]]] = []

    def add_get(self, endpoint: str, response: Any) -> "StubHtbHttpRequest":
        self.get_routes.setdefault(endpoint, []).append(response)
        return self

    def add_get_sequence(self, endpoint: str, responses: List[Any]) -> "StubHtbHttpRequest":
        self.get_routes.setdefault(endpoint, []).extend(list(responses))
        return self

    def add_post(self, endpoint: str, response: Any) -> "StubHtbHttpRequest":
        self.post_routes.setdefault(endpoint, []).append(response)
        return self

    def endpoints_for(self, method: str) -> List[str]:
        return [call[1] for call in self.calls if call[0] == method]

    def _pop_response(self, routes: Dict[str, List[Any]], endpoint: str) -> Any:
        if endpoint not in routes or len(routes[endpoint]) == 0:
            raise AssertionError(f"Unexpected call to {endpoint}")

        response = routes[endpoint].pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def get_request(self, endpoint: str | None = None, download: bool = False, base: str | None = None, custom_url: str | None = None) -> Any:
        key = custom_url if custom_url is not None else endpoint
        self.calls.append(("GET", key, {"endpoint": endpoint, "download": download, "custom_url": custom_url}))
        return self._pop_response(self.get_routes, key)

    def post_request(self, endpoint: str, json: Any = None, api_version: str = "v4") -> Any:
        self.calls.append(("POST", endpoint, {"json": json, "api_version": api_version}))
        return self._pop_response(self.post_routes, endpoint)


@pytest.fixture(autouse=True)
def reset_client_caches() -> None:
    client_mod._user_cache = {}
    client_mod._vpn_server_cache = {}
    yield
    client_mod._user_cache = {}
    client_mod._vpn_server_cache = {}


@pytest.fixture()
def stub_http() -> StubHtbHttpRequest:
    return StubHtbHttpRequest()


@pytest.fixture()
def client(stub_http: StubHtbHttpRequest) -> HTBClient:
    return HTBClient(stub_http)
