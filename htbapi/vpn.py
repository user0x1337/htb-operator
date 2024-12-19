import os
import tempfile
from typing import Optional, cast

from htbapi import client, CannotSwitchWithActive, VpnException, MachineInfo, RequestException

class BaseVpnServer(client.BaseHtbApiObject):
    is_assigned: bool
    name: Optional[str]
    current_clients: int
    location: Optional[str]  # e.g. EU, US, AU, ...

    # noinspection PyUnresolvedReferences
    def __init__(self, _client: "HTBClient"):
        self._client = _client
        self.is_assigned = False

    def switch(self) -> "BaseVpnServer":
        """Switches the client to use this VPN server"""
        try:
            data: dict = self._client.htb_http_request.post_request(endpoint=f'connections/servers/switch/{self.id}')
        except RequestException as e:
            raise VpnException(e.args[0]["message"])

        if "active machine before switching VPN" in data["message"]:
            raise CannotSwitchWithActive(data["message"])

        if data.get("status") is True:
            if "data" in data:
                self.name = data["data"].get('friendly_name')
                self.current_clients =  data["data"].get('current_clients', 0)
                self.location =  data["data"].get('location')

                return self

        raise VpnException(data["message"])


    def download(self, path: Optional[str] = None, tcp: bool = False) -> str:
        """Download the OpenVPN file to the corresponding server"""
        if path is None:
            fd, path = tempfile.mkstemp(suffix='.ovpn')
            os.close(fd)

        url = f'access/ovpnfile/{self.id}/0'
        if tcp:
            url += '/1'

        # I cannot download a VPN file for servers I am not assigned to
        if not self.is_assigned:
            self.switch()

        try:
            data = self._client.htb_http_request.get_request(endpoint=url, download=True)
        except RequestException as e:
            if len(e.args) > 0 and "message" in e.args[0]:
                data = e.args[0]["message"].encode()
            else:
                raise e

        # Still not assigned? - Switch again and try a last time.
        if b"You are not assigned" in data:
            self.switch()
            # Try again
            data = self._client.htb_http_request.get_request(endpoint=url, download=True)

        data:bytes = cast(bytes, data)
        with open(path, 'wb') as f:
            f.write(data)

        return path

    # noinspection PyUnresolvedReferences
    @staticmethod
    def download_ovpn_file(vpn_id: int,
                           _client: "HTBClient",
                           path: Optional[str] = None,
                           tcp: bool = False) -> str:
        """Download the OpenVPN file to the corresponding server"""
        data: dict = {"id": vpn_id}
        return VpnServerInfo(_client=_client, data=data).download(path=path, tcp=tcp)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def switch_vpn_server(vpn_id: int,
                          _client: "HTBClient") -> "BaseVpnServer":
        """Switches the client to use this VPN server"""
        data: dict = {"id": vpn_id}
        return VpnServerInfo(_client=_client, data=data).switch()


class VpnServerInfo(BaseVpnServer):
    location_type_friendly: Optional[str]
    full: bool
    product: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(_client=_client)
        self.id = data.get('id')
        self.name = data.get('friendly_name')
        self.full = data.get('full', False)
        self.current_clients = data.get('current_clients', 0)
        self.location = data.get('location')
        self.location_type_friendly = data.get('location_type_friendly', None)
        self.is_assigned = data.get('is_assigned', False)
        self.product = data.get('product', "")


    def __repr__(self):
        return f"<VpnServerInfo '{self.name} | {self.id}'>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "full": self.full,
            "current_clients": self.current_clients,
            "location": self.location,
            "location_type_friendly": self.location_type_friendly,
            "is_assigned": self.is_assigned,
            "product": self.product,
        }

class VpnConnection(client.BaseHtbApiObject):
    """VPN connection"""
    type: str  # e.g. "Fortress", "VIP+", ...
    name: str
    server_id: int
    server_hostname: str
    server_port: Optional[int]
    server_name: str
    connection_username: str
    connection_through_pwnbox: bool
    connection_ipv4: str
    connection_ipv6: str
    connection_down: float # in bytes
    connection_up: float # in bytes

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.type = data.get('type')
        self.name = data.get('location_type_friendly')
        self.server_id = data["server"]['id']
        self.server_hostname = data["server"]['hostname']
        self.server_port = data["server"].get('port', None)
        self.server_name = data["server"]['friendly_name']
        self.connection_username = data["connection"]['name']
        self.connection_through_pwnbox = data["connection"]['through_pwnbox']
        self.connection_ipv4 = data["connection"]['ip4']
        self.connection_ipv6 = data["connection"]['ip6']
        self.connection_down = data["connection"]['down']
        self.connection_up = data["connection"]['up']

    def __repr__(self):
        return f"<VpnConnection '{self.name}'>"

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "name": self.name,
            "server_id": self.server_id,
            "server_hostname": self.server_name,
            "server_port": self.server_port,
            "server_name": self.server_name,
            "connection_username": self.connection_username,
            "connection_through_pwnbox": self.connection_through_pwnbox,
            "connection_ipv4": self.connection_ipv4,
            "connection_ipv6": self.connection_ipv6,
            "connection_down": self.connection_down,
            "connection_up": self.connection_up
        }

class AccessibleVpnServer(BaseVpnServer):
    """Accessible VPN server"""
    type: str
    can_access: bool
    server_id: int
    server_name: Optional[str]
    machine: Optional[MachineInfo]
    pro_lab_name: Optional[str]
    pro_lab_id: Optional[int]

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        super().__init__(_client=_client)

        self.type = data.get('type')
        self.is_assigned = True
        self.can_access = data.get('can_access', False)

        if data.get("assigned_server", None) is not None:
            self.id = data["assigned_server"]['id']
            self.name = data["assigned_server"]['friendly_name']
            self.current_clients = data["assigned_server"]['current_clients']
            self.location = data["assigned_server"]['location']
            self.machine = None
        else:
            self.id = 0
            self.name = None
            self.current_clients = 0
            self.location = None
            self.machine = None

        if self.type == "release_arena" and "machine" in data:
            self.machine = self._client.get_machine(data["machine"]["id"])

        if self.type == "prolabs" and "pro_lab" in data:
            self.pro_lab_id = data["pro_lab"].get('id', None)
            self.pro_lab_name = data["pro_lab"]['name']


    def __repr__(self):
        return f"<AccessibleVpnServer '{self.type} | {self.name if self.name is not None else self.pro_lab_name}'>"

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "can_access": self.can_access,
            "current_clients": self.current_clients,
            "server_location": self.location,
            "server_id": self.server_id,
            "server_name": self.name,
            "machine": None if self.machine is None else self.machine.to_dict(),
            "pro_lab_id": self.pro_lab_id,
            "pro_lab_name": self.pro_lab_name,
        }
