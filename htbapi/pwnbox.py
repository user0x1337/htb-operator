import datetime

import dateutil.parser

from htbapi import client, RequestException, NoPwnBoxActiveException


class PwnboxUsage(client.BaseHtbApiObject):
    minutes: int
    sessions: int
    allowed_minutes: int
    remaining_minutes: int
    used: int
    total: int
    active_minutes: int

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.minutes = data.get("minutes", 0)
        self.sessions = data.get("sessions", 0)
        self.allowed_minutes = data.get("allowed", 0)
        self.remaining_minutes = data.get("remeaining", 0)
        self.used = data.get("used", 0)
        self.total = data.get("total", 0)
        self.active_minutes = data.get("active_minutes", 0)

    def __repr__(self):
        return f"<PwnboxUsage {self.remaining_minutes}>"

    def to_dict(self):
        return {
            "minutes": self.minutes,
            "sessions": self.sessions,
            "allowed_minutes": self.allowed_minutes,
            "remaining_minutes": self.remaining_minutes,
            "used": self.used,
            "total": self.total,
            "active_minutes": self.active_minutes,
        }



class PwnboxStatus(client.BaseHtbApiObject):
    flock_id: int
    hostname: str
    username: str
    vnc_password: str
    vnc_view_only_password: str
    status: str
    is_ready: bool
    location: str
    proxy_url: str
    spectate_url: str
    life_remaining: int
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.id = data.get("id", 0)
        self.flock_id = data.get("flock_id", 0)
        self.hostname = data.get("hostname", "")
        self.username = data.get("username", "")
        self.vnc_password = data.get("vnc_password", "")
        self.vnc_view_only_password = data.get("vnc_view_only_password", "")
        self.status = data.get("status", "")
        self.is_ready = data.get("is_ready", False)
        self.location = data.get("location", "")
        self.proxy_url = data.get("proxy_url", "")
        self.spectate_url = data.get("spectate_url", "")
        self.life_remaining = data.get("life_remaining", 0)
        self.expires_at = dateutil.parser.parse(data.get("expires_at")).replace(tzinfo=datetime.timezone.utc)
        self.created_at = dateutil.parser.parse(data.get("created_at")).replace(tzinfo=datetime.timezone.utc)
        self.updated_at = dateutil.parser.parse(data.get("updated_at")).replace(tzinfo=datetime.timezone.utc)

    def terminate(self) -> [bool, str]:
        """Terminate an active Pwnbox session. Returns an exception if termination fails."""
        try:
            data: dict = self._client.htb_http_request.post_request(endpoint="pwnbox/terminate")
            if data is None or len(data) == 0 or len(data.keys()) == 0:
                return True, ""

            return False, data["error"] if "error" in data else ""
        except RequestException as e:
            raise NoPwnBoxActiveException(e)

    def __repr__(self):
        return f"<PwnboxStatus {self.id} | {self.hostname} | {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "hostname": self.hostname,
            "username": self.username,
            "vnc_password": self.vnc_password,
            "vnc_view_only_password": self.vnc_view_only_password,
            "status": self.status,
            "is_ready": self.is_ready,
            "location": self.location,
            "proxy_url": self.proxy_url,
            "spectate_url": self.spectate_url,
            "life_remaining": self.life_remaining,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }