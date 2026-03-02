from __future__ import annotations

import pytest

from htbapi.exception.errors import CannotSwitchWithActive, RequestException
from htbapi.vpn import VpnServerInfo, BaseVpnServer


def vpn_server_data(server_id: int = 10, assigned: bool = False) -> dict:
    return {
        "id": server_id,
        "friendly_name": "EU-1",
        "current_clients": 0,
        "location": "EU",
        "is_assigned": assigned,
    }


def switch_response() -> dict:
    return {
        "status": True,
        "data": {
            "friendly_name": "EU-1",
            "current_clients": 1,
            "location": "EU",
        },
        "message": "ok",
    }


def test_vpn_switch_raises_when_active_machine(client, stub_http) -> None:
    vpn = VpnServerInfo(_client=client, data=vpn_server_data())
    stub_http.add_post(
        f"connections/servers/switch/{vpn.id}",
        {"message": "active machine before switching VPN"},
    )

    with pytest.raises(CannotSwitchWithActive):
        vpn.switch()


def test_vpn_download_switches_when_not_assigned(client, stub_http, tmp_path) -> None:
    vpn = VpnServerInfo(_client=client, data=vpn_server_data(assigned=False))
    stub_http.add_post(f"connections/servers/switch/{vpn.id}", switch_response())
    stub_http.add_get(f"access/ovpnfile/{vpn.id}/0", b"OVPN")

    output_path = vpn.download(path=str(tmp_path / "vpn.ovpn"))

    assert (tmp_path / "vpn.ovpn").read_bytes() == b"OVPN"
    assert output_path.endswith("vpn.ovpn")


def test_vpn_download_retries_when_still_unassigned(client, stub_http, tmp_path) -> None:
    vpn = VpnServerInfo(_client=client, data=vpn_server_data(assigned=False))
    stub_http.add_post(f"connections/servers/switch/{vpn.id}", switch_response())
    stub_http.add_get(
        f"access/ovpnfile/{vpn.id}/0",
        RequestException({"message": "You are not assigned to this server"}),
    )
    stub_http.add_post(f"connections/servers/switch/{vpn.id}", switch_response())
    stub_http.add_get(f"access/ovpnfile/{vpn.id}/0", b"OVPN-OK")

    output_path = vpn.download(path=str(tmp_path / "retry.ovpn"))

    assert (tmp_path / "retry.ovpn").read_bytes() == b"OVPN-OK"
    assert output_path.endswith("retry.ovpn")


def test_vpn_download_ovpn_file_static_helper(client, stub_http, tmp_path) -> None:
    stub_http.add_post("connections/servers/switch/55", switch_response())
    stub_http.add_get("access/ovpnfile/55/0", b"DATA")

    output_path = BaseVpnServer.download_ovpn_file(55, _client=client, path=str(tmp_path / "x.ovpn"))

    assert (tmp_path / "x.ovpn").read_bytes() == b"DATA"
    assert output_path.endswith("x.ovpn")
