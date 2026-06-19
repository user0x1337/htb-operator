from __future__ import annotations

from typing import Any, Dict, List, Tuple

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Imports that transitively require httpx must not happen at module level,
# otherwise loading conftest.py would already fail if httpx is missing.
# Instead, they are performed inside fixtures (with try/except).

# Create a lightweight stub module "htbapi" if real dependencies are missing.
# This stub provides commonly imported top‑level symbols and still allows
# targeted imports of submodules like htbapi.client or htbapi.challenge via the
# real package path (without executing htbapi/__init__.py).
try:
    import htbapi as _real_htbapi  # type: ignore
    _ = _real_htbapi  # noqa: F401
except Exception:
    import types as _types
    import sys as _sys

    if "htbapi" not in _sys.modules:
        _pkg = _types.ModuleType("htbapi")
        _pkg.__path__ = [str(ROOT / "htbapi")]  # expose real package files

        # Top-level classes/exceptions imported by the code
        class RequestException(Exception):  # type: ignore
            def __init__(self, data):
                super().__init__(str(data))
                self.data = data

            def __str__(self):
                if isinstance(self.data, dict) and "message" in self.data:
                    return self.data["message"]
                return super().__str__()

        class NoPwnBoxActiveException(Exception):
            pass

        class IncorrectArgumentException(Exception):
            pass

        class CannotSwitchWithActive(Exception):
            pass

        class VpnException(Exception):
            pass

        class BaseHtbHttpRequest:  # Dummy for signatures
            pass

        class HtbHtbHttpRequest(BaseHtbHttpRequest):  # Dummy for signatures
            def __init__(self, *args, **kwargs):
                pass

        class HTBClient:  # Dummy for command.base type reference
            def __init__(self, *args, **kwargs):
                pass

        class User:  # for console/commands type references
            def __init__(self, id: int = 0, name: str = ""):
                self.id = id
                self.name = name

            def to_dict(self, key_filter=None):
                return {"ID": self.id, "Name": self.name or "user"}

        class Activity:  # for panels
            pass

        class FortressUserProfile:
            pass

        class ProLabUserProfile:
            pass

        class EndgameUserProfile:
            pass

        class SherlockUserProfile:
            pass

        class MachineOsUserProfile:
            pass

        class ChallengeUserProfile:
            pass

        class Certificate:
            def __init__(self, cert_id: int = 0, name: str = "", downloaded: bool = False, created_at=None):
                from datetime import datetime, timezone
                self.cert_id = cert_id
                self.name = name
                self.has_downloaded_cert = downloaded
                self.created_at = created_at or datetime(1970, 1, 1, tzinfo=timezone.utc)

        class ProLabInfo:
            def __init__(self, name: str = "Prolab", id: int = 0):
                self.name = name
                self.id = id

            def to_dict(self):
                return {"name": self.name, "id": self.id}

        class PwnboxStatus:
            def __init__(self):
                self.id = 0
                self.hostname = "pwnbox"
                self.username = "user"
                self.vnc_password = "pass"
                self.spectate_url = "https://example.invalid/?password=foo&view_only=true"

            def to_dict(self):
                return {
                    "id": self.id,
                    "hostname": self.hostname,
                    "username": self.username,
                    "vnc_password": self.vnc_password,
                    "spectate_url": self.spectate_url,
                }

            def terminate(self):
                return True, "terminated"

        # Season models
        class SeasonList:
            def __init__(self, id: int = 1, name: str = "Season 1", start_date=None, end_date=None, active: bool = True):
                import datetime as _dt
                self.id = id
                self.name = name
                self.start_date = start_date or _dt.datetime(2024, 1, 1, tzinfo=_dt.timezone.utc)
                self.end_date = end_date
                self.active = active

            def to_dict(self):
                return {
                    "id": self.id,
                    "name": self.name,
                    "start_date": self.start_date,
                    "end_date": self.end_date,
                    "active": self.active,
                }

        class SeasonUserDetails:
            def __init__(self):
                self.season_id = 1
                self.name = "Season 1"
                self.tier = "Bronze"
                self.user_name = "user"
                self.current_rank = 100
                self.total_ranks = 1000
                self.user_flags_pawned = 1
                self.user_bloods_pawned = 0
                self.root_flags_pawned = 1
                self.root_bloods_pawned = 0
                self.total_machines = 10

            def to_dict(self):
                return {
                    "season_id": self.season_id,
                    "name": self.name,
                    "tier": self.tier,
                    "user_name": self.user_name,
                    "current_rank": self.current_rank,
                    "total_ranks": self.total_ranks,
                    "user_flags_pawned": self.user_flags_pawned,
                    "user_bloods_pawned": self.user_bloods_pawned,
                    "root_flags_pawned": self.root_flags_pawned,
                    "root_bloods_pawned": self.root_bloods_pawned,
                    "total_machines": self.total_machines,
                }

        class SeasonMachine:
            def __init__(self, name: str = "Machine 1", release_date=None):
                import datetime as _dt
                self.name = name
                self.release_date = release_date or _dt.datetime(2024, 1, 10, tzinfo=_dt.timezone.utc)

            def to_dict(self):
                return {"name": self.name, "release_date": self.release_date}

        class SherlockCategory:
            def __init__(self, name: str = "Web"):
                self.name = name

            def to_dict(self):
                return {"name": self.name}

        class SherlockInfo:
            def __init__(self, name: str = "Sherlock 1", retired: bool = False, category: SherlockCategory | None = None):
                self.name = name
                self.retired = retired
                self.category = category or SherlockCategory()

            @property
            def state(self):
                return "retired" if self.retired else "active"

            def to_dict(self):
                return {"name": self.name, "state": self.state, "category": self.category.to_dict()}

        # Im Stub-Modul registrieren
        _pkg.RequestException = RequestException
        _pkg.NoPwnBoxActiveException = NoPwnBoxActiveException
        _pkg.IncorrectArgumentException = IncorrectArgumentException
        _pkg.CannotSwitchWithActive = CannotSwitchWithActive
        _pkg.VpnException = VpnException
        _pkg.BaseHtbHttpRequest = BaseHtbHttpRequest
        _pkg.HtbHtbHttpRequest = HtbHtbHttpRequest
        _pkg.HTBClient = HTBClient
        _pkg.User = User
        _pkg.Activity = Activity
        _pkg.FortressUserProfile = FortressUserProfile
        _pkg.ProLabUserProfile = ProLabUserProfile
        _pkg.EndgameUserProfile = EndgameUserProfile
        _pkg.SherlockUserProfile = SherlockUserProfile
        _pkg.MachineOsUserProfile = MachineOsUserProfile
        _pkg.ChallengeUserProfile = ChallengeUserProfile
        _pkg.Certificate = Certificate
        _pkg.ProLabInfo = ProLabInfo
        _pkg.PwnboxStatus = PwnboxStatus
        _pkg.SeasonList = SeasonList
        _pkg.SeasonUserDetails = SeasonUserDetails
        _pkg.SeasonMachine = SeasonMachine
        _pkg.SherlockCategory = SherlockCategory
        _pkg.SherlockInfo = SherlockInfo

        # Weitere ggf. von Commands verwendete Top-Level-Modelle
        class BadgeCategory:
            def __init__(self, name: str = ""):
                self.name = name

            def to_dict(self):
                return {"name": self.name}

        _pkg.BadgeCategory = BadgeCategory

        _sys.modules["htbapi"] = _pkg


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

    def get_request(self, endpoint: str | None = None, download: bool = False, base: str | None = None, custom_url: str | None = None, api_version: str = "v4") -> Any:
        key = custom_url if custom_url is not None else endpoint
        self.calls.append(("GET", key, {"endpoint": endpoint, "download": download, "custom_url": custom_url, "api_version": api_version}))
        return self._pop_response(self.get_routes, key)

    def post_request(self, endpoint: str, json: Any = None, api_version: str = "v4") -> Any:
        self.calls.append(("POST", endpoint, {"json": json, "api_version": api_version}))
        return self._pop_response(self.post_routes, endpoint)


@pytest.fixture(autouse=True)
def reset_client_caches() -> None:
    """Reset caches from htbapi.client if module/dependencies are available.

    If optional dependencies (e.g., httpx) are missing, test collection should
    still work — in that case do nothing silently.
    """
    try:
        import htbapi.client as client_mod  # type: ignore
        client_mod._user_cache = {}
        client_mod._vpn_server_cache = {}
        yield
        client_mod._user_cache = {}
        client_mod._vpn_server_cache = {}
    except Exception:
        # Module/dependency not available — allow tests that don't need it to run.
        yield


@pytest.fixture()
def stub_http() -> StubHtbHttpRequest:
    return StubHtbHttpRequest()


@pytest.fixture()
def client(stub_http: StubHtbHttpRequest):
    """Provide an HTBClient if the library is available.

    If required dependencies are missing, skip dependent tests instead of
    failing during import of conftest.py.
    """
    try:
        from htbapi import HTBClient  # type: ignore
    except Exception:
        pytest.skip("HTBClient/dependencies not available — test skipped")
    return HTBClient(stub_http)
