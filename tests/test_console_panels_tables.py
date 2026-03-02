from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from rich.console import Console

import console.cli_panel as panel_mod
import console.cli_table as table_mod


def _render_text(renderable) -> str:
    console = Console(record=True, width=220)
    console.print(renderable)
    return console.export_text()


def _dt(days: int = 0) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(days=days)


def test_format_bool_variants() -> None:
    assert panel_mod.format_bool(True) == "✔"
    assert panel_mod.format_bool(False) == "✘"
    assert panel_mod.format_bool(True, color_true="green") == "[green]✔[/green]"
    assert panel_mod.format_bool(False, color_false="red") == "[red]✘[/red]"
    assert panel_mod.format_bool("x") == "x"


def test_get_expire_str_none_and_valid_timestamp() -> None:
    assert panel_mod.get_expire_str(None) == "-"
    value = panel_mod.get_expire_str(_dt(days=1))
    assert "UTC (" in value
    assert "left)" in value


def test_create_custom_panel_renders_key_and_bool() -> None:
    panel = panel_mod._create_custom_panel(
        custom_dict={"Enabled": True, "Name": "alpha"},
        panel_title="Test Panel",
        target_height=4,
    )
    text = _render_text(panel)
    assert "Test Panel" in text
    assert "Enabled" in text
    assert "alpha" in text
    assert "✔" in text


def test_create_activity_panel_sorts_and_limits_entries() -> None:
    activities = [
        SimpleNamespace(
            date=_dt(days=-3),
            date_diff="3d",
            object_type="machine",
            type="user",
            name="old-entry",
            points=5,
            flag_title=None,
            challenge_category=None,
        ),
        SimpleNamespace(
            date=_dt(days=-1),
            date_diff="1d",
            object_type="challenge",
            type="root",
            name="newer-entry",
            points=10,
            flag_title=None,
            challenge_category="Web",
        ),
        SimpleNamespace(
            date=_dt(days=-2),
            date_diff="2d",
            object_type="endgame",
            type="user",
            name="middle-entry",
            points=7,
            flag_title="FLAG-A",
            challenge_category=None,
        ),
    ]

    panel = panel_mod.create_activity_panel(activities, limit_activity_entries=2)
    text = _render_text(panel)

    assert "newer-entry" in text
    assert "middle-entry" in text
    assert "old-entry" not in text


def test_create_sherlock_group_panel_contains_active_and_retired() -> None:
    sherlocks = [
        {
            "id": 1,
            "name": "Alpha",
            "category_name": "Web",
            "difficulty": "Easy",
            "rating": 4.2,
            "is_owned": True,
            "progress": 100,
            "release_date": _dt(days=-20),
            "state": "active",
        },
        {
            "id": 2,
            "name": "Bravo",
            "category_name": "Forensic",
            "difficulty": "Medium",
            "rating": 3.2,
            "is_owned": False,
            "progress": 20,
            "release_date": _dt(days=-40),
            "state": "retired",
        },
    ]

    panel_group = panel_mod.create_sherlock_list_group_by_retired_panel(sherlocks)
    text = _render_text(panel_group)

    assert "Active" in text
    assert "Retired" in text
    assert "Alpha" in text
    assert "Bravo" in text


def test_create_panel_active_machine_status_renders_machine_data() -> None:
    active_machine = {
        "id": 13,
        "name": "Forest",
        "ip": "10.10.10.10",
        "expires_at": _dt(days=1),
        "retired": False,
        "os": "Linux",
        "info_status": "ready",
        "points": 20,
        "user_owned": True,
        "root_owned": False,
        "difficulty": "Medium",
        "vpn_server": "EU-1",
        "vpn_server_id": 99,
        "num_players": 15,
        "num_solved": 500,
        "hosts_file_name": "forest.htb",
    }

    panel = panel_mod.create_panel_active_machine_status(active_machine)
    text = _render_text(panel)
    assert "Active Machine" in text
    assert "Forest" in text
    assert "10.10.10.10" in text


def test_create_vpn_list_table_sorts_servers() -> None:
    vpn_servers = [
        {
            "product": "release_arena",
            "location": "US",
            "id": 3,
            "name": "US-B",
            "is_assigned": False,
            "current_clients": 20,
            "full": False,
        },
        {
            "product": "labs",
            "location": "EU",
            "id": 1,
            "name": "EU-A",
            "is_assigned": True,
            "current_clients": 5,
            "full": False,
        },
    ]
    panel = table_mod.create_vpn_list_table(vpn_servers)
    text = _render_text(panel)

    first = text.find("EU-A")
    second = text.find("US-B")
    assert first != -1 and second != -1
    assert first < second


def test_create_table_active_vpn_connections_contains_values() -> None:
    rows = [
        {
            "type": "VIP",
            "name": "EU-1",
            "server_id": 5,
            "server_hostname": "host.htb",
            "server_port": 1337,
            "server_name": "EU #1",
            "connection_through_pwnbox": False,
            "connection_ipv4": "10.10.14.5",
            "connection_ipv6": "::1",
            "interface": "tun0",
            "current_clients": 42,
        }
    ]
    table = table_mod.create_table_active_vpn_connections(rows)
    text = _render_text(table)
    assert "Active VPN-Connections" in text
    assert "EU-1" in text
    assert "tun0" in text


def test_create_benchmark_table_renders_hostname_and_title() -> None:
    data = [
        {
            "latency": 32.5,
            "id": 5,
            "hostname": "vpn.eu.htb",
            "product": "labs",
            "name": "EU #1",
            "location": "EU",
            "current_clients": 8,
            "is_assigned": True,
        }
    ]
    panel = table_mod.create_benchmark_table(data)
    text = _render_text(panel)
    assert "Benchmark Results" in text
    assert "vpn.eu.htb" in text


def test_create_season_list_table_renders_seasons() -> None:
    seasons = [
        {
            "id": 1,
            "name": "Season 1",
            "start_date": _dt(days=-120),
            "end_date": _dt(days=-90),
            "state": "ended",
            "active": False,
        },
        {
            "id": 2,
            "name": "Season 2",
            "start_date": _dt(days=-10),
            "end_date": None,
            "state": "running",
            "active": True,
        },
    ]
    panel = table_mod.create_season_list_table(seasons)
    text = _render_text(panel)
    assert "Seasons Overview" in text
    assert "Season 1" in text
    assert "Season 2" in text


def test_create_machine_list_table_handles_unknown_and_known_rows() -> None:
    machine_info = [
        {
            "id": 1,
            "name": "Known",
            "difficulty": "Easy",
            "release_date": _dt(days=-2),
            "is_owned_user": True,
            "is_owned_root": False,
            "user_points": 10,
            "root_points": 20,
            "unknown": False,
        },
        {
            "id": -1,
            "name": "Unknown",
            "difficulty": "Hard",
            "release_date": _dt(days=5),
            "is_owned_user": False,
            "is_owned_root": False,
            "user_points": 0,
            "root_points": 0,
            "unknown": True,
        },
    ]
    panel = table_mod.create_machine_list_table(machine_info=machine_info, season_name="Season X")
    text = _render_text(panel)
    assert "Season X" in text
    assert "Known" in text

    table = panel.renderable
    name_cells = table.columns[2]._cells
    assert "Known" in name_cells[0]
    assert "-" in name_cells[1]


def test_create_table_badge_list_skips_empty_categories() -> None:
    categories = [
        {"name": "Empty", "badges": []},
        {
            "name": "Web",
            "badges": [
                {
                    "id": 1,
                    "name": "Badge A",
                    "description": "desc",
                    "users_count": 100,
                    "rarity": 0.1,
                    "badge_obtained": True,
                    "badge_obtained_datetime": _dt(days=-1),
                }
            ],
        },
    ]
    group = table_mod.create_table_badge_list(categories)
    text = _render_text(group)
    assert "Web" in text
    assert "Badge A" in text
    assert "Empty" not in text


def test_create_table_challenge_list_groups_by_category() -> None:
    challenges = [
        {
            "id": 1,
            "name": "Web 101",
            "difficulty": "Easy",
            "avg_difficulty": 2,
            "points": 20,
            "solved": False,
            "retired": False,
            "rating": 4.3,
            "isTodo": True,
            "release_date": _dt(days=-30),
            "category_id": 1,
            "state": "active",
        },
        {
            "id": 2,
            "name": "Crypto 101",
            "difficulty": "Medium",
            "avg_difficulty": 3,
            "points": 30,
            "solved": True,
            "retired": True,
            "rating": 4.0,
            "isTodo": False,
            "release_date": _dt(days=-20),
            "category_id": 2,
            "state": "active",
        },
    ]
    category_dict = {1: "web", 2: "crypto"}
    group = table_mod.create_table_challenge_list(challenge_list=challenges, category_dict=category_dict)
    text = _render_text(group)
    assert "Web" in text
    assert "Crypto" in text
    assert "Web 101" in text
    assert "Crypto 101" in text


def test_create_machine_list_group_by_retired_covers_sections() -> None:
    machines = [
        {
            "id": 1,
            "name": "ActiveBox",
            "os": "Linux",
            "difficultyText": "Easy",
            "stars": 4.5,
            "authUserInUserOwns": True,
            "authUserInRootOwns": False,
            "retired": False,
            "release_date": _dt(days=-10),
        },
        {
            "id": 2,
            "name": "RetiredBox",
            "os": "Windows",
            "difficultyText": "Hard",
            "stars": 4.1,
            "authUserInUserOwns": False,
            "authUserInRootOwns": False,
            "retired": True,
            "release_date": _dt(days=-20),
            "retiring": True,
        },
        {
            "id": 3,
            "name": "ScheduledBox",
            "os": "Linux",
            "difficultyText": "Medium",
            "stars": 3.8,
            "authUserInUserOwns": False,
            "authUserInRootOwns": False,
            "retired": False,
            "release_date": _dt(days=20),
        },
    ]
    group = table_mod.create_machine_list_group_by_retired(machines)
    text = _render_text(group)
    assert "Active" in text
    assert "Retired" in text
    assert "Scheduled" in text
    assert "ActiveBox" in text
    assert "RetiredBox" in text
    assert "ScheduledBox" in text


def test_create_machine_list_group_by_os_covers_multiple_os() -> None:
    machines = [
        {
            "id": 1,
            "name": "Lnx",
            "os": "Linux",
            "difficultyText": "Easy",
            "stars": 4.5,
            "authUserInUserOwns": False,
            "authUserInRootOwns": False,
            "retired": False,
            "release_date": _dt(days=-5),
        },
        {
            "id": 2,
            "name": "Win",
            "os": "Windows",
            "difficultyText": "Medium",
            "stars": 4.0,
            "authUserInUserOwns": False,
            "authUserInRootOwns": False,
            "retired": False,
            "release_date": _dt(days=-4),
        },
    ]
    group = table_mod.create_machine_list_group_by_os(machines)
    text = _render_text(group)
    assert "Linux" in text
    assert "Windows" in text
    assert "Lnx" in text
    assert "Win" in text


@pytest.mark.parametrize(
    "value",
    [
        "x",
        0,
    ],
)
def test_format_bool_non_bool_passthrough(value) -> None:
    assert panel_mod.format_bool(value) == value
