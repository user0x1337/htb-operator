from datetime import datetime, timezone
from typing import List, Set

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from console.cli_panel import format_bool

type: str  # e.g. "Fortress", "VIP+", ...
name: str
server_id: int
server_hostname: str
server_port: int
server_name: str
connection_username: str
connection_through_pwnbox: bool
connection_ipv4: str
connection_ipv6: str
connection_down: float  # in bytes
connection_up: float  # in bytes


def create_season_list_table(seasons: list) -> Table | Panel:
    table = Table(expand=True, show_lines=False, box=None)
    table.add_column(header="#", justify="left")
    table.add_column(header="ID", justify="left")
    table.add_column(header="Name", justify="left")
    table.add_column(header="Start date/time", justify="left")
    table.add_column(header="End date/time", justify="left")
    table.add_column(header="State", justify="left")
    table.add_column(header="Active?", justify="left")

    for i, res in enumerate(seasons):
        color_begin = ""
        color_end = ""
        if res["state"] == "upcoming":
            color_begin = "[bold bright_magenta]"
            color_end = "[/bold bright_magenta]"
        elif res["state"] != "ended":
            color_begin = "[bold bright_green]"
            color_end = "[/bold bright_green]]"

        table.add_row(f'{color_begin}{i + 1}{color_end}',
                      f'{color_begin}{res["id"]}{color_end}',
                      f'{color_begin}{res["name"]}{color_end}',
                      f'{color_begin}{res["start_date"].strftime("%Y-%m-%d %H:%M")} UTC{color_end}',
                      f'{color_begin}{"-" if res["end_date"] is None else res["end_date"].strftime("%Y-%m-%d %H:%M")} UTC{color_end}',
                      f'{color_begin}{res["state"]}{color_end}',
                      f'{color_begin}{format_bool(res["active"])}{color_end}')
    return Panel(table,
                 title=f"[bold yellow]Seasons Overview[/bold yellow]",
                 border_style="yellow",
                 title_align="left",
                 expand=False)

def create_benchmark_table(vpn_benchmark_results: list) -> Table | Panel:
    """Create benchmark table"""
    table = Table(expand=True, show_lines=False, box=None)
    table.add_column(header="#",justify="left")
    table.add_column(header="Latency [ms]", justify="left")
    table.add_column(header="VPN-ID", justify="center")
    table.add_column(header="Hostname", justify="left")
    table.add_column(header="Product", justify="left")
    table.add_column(header="Servername", justify="left")
    table.add_column(header="Location", justify="left")
    table.add_column(header="# Clients", justify="center")
    table.add_column(header="Assigned?", justify="center")

    for i, res in enumerate(vpn_benchmark_results):
        latency = res['latency']
        if res["latency"] < 50:
            latency = f'[bold bright_green]{latency}ms[/bold bright_green]'
        elif res["latency"] < 120:
            latency = f'[bold bright_yellow]{latency}ms[/bold bright_yellow]'
        else:
            latency = f'[bold bright_red]{latency}ms[/bold bright_red]'

        current_clients = res['current_clients']
        if res["current_clients"] < 20:
            current_clients = f'[bold bright_green]{current_clients}[/bold bright_green]'
        elif res["current_clients"] < 50:
            current_clients = f'[bold bright_yellow]{current_clients}[/bold bright_yellow]'
        else:
            current_clients = f'[bold bright_red]{current_clients}[/bold bright_red]'

        table.add_row(f'{i + 1}',
                      f'{latency}',
                      f'{res["id"]}',
                      f'{res["hostname"]}',
                      f'{res["product"]}',
                      f'{res["name"]}',
                      f'{res["location"]}',
                      f'{current_clients}',
                      f'{format_bool(res["is_assigned"])}')
    return Panel(table,
                 title=f"[bold yellow]Benchmark Results[/bold yellow]",
                 border_style="yellow",
                 title_align="left",
                 expand=False)

def create_vpn_list_table(vpn_servers: list[dict]) -> Table | Panel:
    assert vpn_servers is not None
    vpn_servers = sorted(vpn_servers, key=lambda x: (x['product'], x['location'], x['name']))

    table = Table(expand=True, show_lines=False, box=None)
    table.add_column(header="#", justify="left")
    table.add_column(header="Product", justify="left")
    table.add_column(header="Location", justify="left")
    table.add_column(header="Server-ID", justify="left")
    table.add_column(header="Name", justify="left")
    table.add_column(header="Assigned?", justify="left")
    table.add_column(header="# Clients", justify="left")
    table.add_column(header="Full?", justify="left")

    for i, vpn_server in enumerate(vpn_servers):
        format_bool_ok_begin = "[bold green]"
        format_bool_ok_end = "[/bold green]"

        table.add_row(f'{i + 1}',
                      f'{vpn_server["product"].replace("_", "-").capitalize()}',
                      f'{vpn_server["location"]}',
                      f'{vpn_server["id"]}',
                      f'{vpn_server["name"]}',
                      f'{format_bool_ok_begin if vpn_server["is_assigned"] else ""}'
                      f'{format_bool(vpn_server["is_assigned"])}'
                      f'{format_bool_ok_end if vpn_server["is_assigned"] else ""}',
                      f'{vpn_server["current_clients"]}',
                      f'{format_bool_ok_begin if vpn_server["full"] else ""}'
                      f'{format_bool(vpn_server["full"])}'
                      f'{format_bool_ok_end if vpn_server["full"] else ""}'
                      )
    return Panel(table,
                 title=f"[bold yellow]VPN-Server[/bold yellow]",
                 border_style="yellow",
                 title_align="left",
                 expand=False)

def create_table_active_vpn_connections(vpn_connections: List[dict]):
    table = Table(title="Active VPN-Connections", show_lines=True)
    table.add_column(header="Type", style="cyan", justify="left")
    table.add_column(header="Name", style="cyan", justify="left")
    table.add_column(header="VPN-Server ID", style="cyan", justify="left")
    table.add_column(header="Server Hostname", style="cyan", justify="left")
    table.add_column(header="Server Port", style="cyan", justify="left")
    table.add_column(header="Server Friendly Name", style="cyan", justify="left")
    table.add_column(header="Through PwnBox", style="cyan", justify="left")
    table.add_column(header="IPv4", style="cyan", justify="left")
    table.add_column(header="IPv6", style="cyan", justify="left")
    table.add_column(header="Interface", style="cyan", justify="left")
    table.add_column(header="# Clients connected", style="cyan", justify="left")

    for vpn_connection in vpn_connections:
        table.add_row(f'{vpn_connection["type"]}',
                      f'{vpn_connection["name"]}',
                      f'{vpn_connection["server_id"]}',
                      f'{vpn_connection["server_hostname"]}',
                      f'{vpn_connection["server_port"]}',
                      f'{vpn_connection["server_name"]}',
                      format_bool(vpn_connection["connection_through_pwnbox"]),
                      f'{vpn_connection["connection_ipv4"]}',
                      f'{vpn_connection["connection_ipv6"]}',
                      f'{vpn_connection["interface"]}',
                      f'{vpn_connection["current_clients"]}'
                      )

    return table


def create_table_badge_list(badge_categories: List[dict]) -> Table | Panel | Group:
    """Create a table with available and obtained badges"""
    panels = []

    for badge_category in badge_categories:
        if len(badge_category["badges"]) == 0:
            continue

        category_name = badge_category["name"]
        table: Table = _create_badge_list_table_header()

        counter = 0
        for badge in badge_category["badges"]:
            counter += 1

            table.add_row(f'{counter}',
                          f'{(badge["id"])}',
                          f'{badge["name"]}',
                          f'{badge["description"]}',
                          f'{badge["users_count"]}',
                          f'{badge["rarity"]}',
                          f'{format_bool(badge["badge_obtained"], color_true="green", color_false="red")}',
                          f'{"" if badge["badge_obtained_datetime"] is None else badge["badge_obtained_datetime"].strftime('%Y-%m-%d')}',
                          )
        panels.append(Panel(table,
                            title=f"[bold yellow]{category_name}[/bold yellow]",
                            border_style="yellow",
                            title_align="left",
                            expand=True))

    return Group(*panels)

def create_table_challenge_list(challenge_list: List[dict], category_dict: dict) -> Table | Panel | Group:
    panels = []
    for k,v in category_dict.items():
        table: Table = _create_challenge_list_table_header()

        filter_type = lambda x: x["category_id"] == k
        if _create_challenge_list_table_rows(table=table, challenge_info=challenge_list, filter_type=filter_type):
            panels.append(Panel(table,
                                title=f"[bold yellow]{v.capitalize()}[/bold yellow]",
                                border_style="yellow",
                                title_align="left",
                                expand=True))

    return Group(*panels)


def _create_challenge_list_table_rows(challenge_info: List[dict], table: Table, filter_type) -> bool:
    found = False
    for i, c in enumerate([c for c in challenge_info if filter_type(c)]):
        found = True

        if "Easy" == c["difficulty"]:
            color = "bright_green"
        elif "Medium" == c["difficulty"]:
            color = "bright_yellow"
        elif "Hard" == c["difficulty"]:
            color = "bright_red"
        elif "Insane" == c["difficulty"]:
            color = "bright_magenta"
        else:
            color = "bright_white"

        retiring: bool = False
        if "retiring" in c and c["retiring"]:
            retiring = True
            retiring_font_begin = "[bold cyan]"
            retiring_font_end = "[/bold cyan]"
        else:
            retiring_font_begin = ""
            retiring_font_end = ""

        table.add_row(f'{retiring_font_begin}{i+1}',
                      f'{retiring_font_begin}[bold {color}]{(c["id"])}[/bold {color}]{retiring_font_end}',
                      f'{retiring_font_begin}[bold {color}]{c["name"]}[/bold {color}]{retiring_font_end}',
                      f'{retiring_font_begin}[bold {color}]{c["difficulty"]}[/bold {color}]{retiring_font_end}',
                      f'{retiring_font_begin}{c["avg_difficulty"]}{retiring_font_end}',
                      f'{retiring_font_begin}{c["points"]}{retiring_font_end}',
                      f'{retiring_font_begin}{format_bool(c["solved"], color_true="green")}{retiring_font_end}',
                      f'{retiring_font_begin}{format_bool(c["retired"], color_true="blue")}{retiring_font_end}',
                      f'{retiring_font_begin}{round(c["rating"], 2)}{retiring_font_end}',
                      f'{retiring_font_begin}{format_bool(c["isTodo"])}{retiring_font_end}',
                      f'{retiring_font_begin}{c["release_date"].strftime('%Y-%m-%d')}{retiring_font_end}'
                      )
    return found


def _create_badge_list_table_header() -> Table:
    table = Table(expand=True, show_lines=False, box=None)

    table.add_column(header="#", width=1)
    table.add_column(header="ID", width=1)
    table.add_column(header="Name", width=10)
    table.add_column(header="Description", width=20)
    table.add_column(header="# Users", justify="center", width=1)
    table.add_column(header="Rarity [%]",  justify="center", width=3)
    table.add_column(header="Obtained?", justify="center", width=3)
    table.add_column(header="Earned date", justify="center", width=10)

    return table


def _create_challenge_list_table_header() -> Table:
    table = Table(expand=True, show_lines=False, box=None)

    table.add_column(header="#", width=1)
    table.add_column(header="ID", width=1)
    table.add_column(header="Name", width=10)
    table.add_column(header="Difficulty", width=4)
    table.add_column(header="Avg Difficulty", width=3)
    table.add_column(header="Points",  justify="center", width=3)
    table.add_column(header="Solved",  justify="center", width=3)
    table.add_column(header="Retired", justify="center", width=3)
    table.add_column(header="Rating",  justify="center", width=3)
    table.add_column(header="TODO", justify="center", width=3)
    table.add_column(header="Release Date", max_width=10)

    return table


def _create_machine_list_table_header() -> Table:
    table = Table(expand=True, show_lines=False, box=None)

    table.add_column("#", width=1)
    table.add_column("ID", width=1)
    table.add_column("Name", width=10)
    table.add_column("OS", width=6)
    table.add_column("Difficulty", width=4)
    table.add_column("\U00002605 Stars", justify="center", width=3)
    table.add_column("Own User?", justify="center", width=3)
    table.add_column("Own Root?", justify="center", width=3)
    table.add_column("Retired?", justify="center", width=3)
    table.add_column("Release date", max_width=10)

    return table


def _create_machine_list_table_rows(machine_info: List[dict], table: Table, filter_type) -> bool:
    found = False
    for i, m in enumerate([m for m in machine_info if filter_type(m)]):
        found = True

        if "Easy" == m["difficultyText"]:
            color = "bright_green"
        elif "Medium" == m["difficultyText"]:
            color = "bright_yellow"
        elif "Hard" == m["difficultyText"]:
            color = "bright_red"
        elif "Insane" == m["difficultyText"]:
            color = "bright_magenta"
        else:
            color = "bright_white"

        if m["os"].lower() == "windows":
            unicode_logo = "\U0001F5D4  "
        elif m["os"].lower() in ["linux", "freebsd", "openbsd"]:
            unicode_logo = "\U0001F427 "
        elif m["os"].lower() == "android":
            unicode_logo = "\U0001F4F1 "
        else:
            unicode_logo = ""

        retiring: bool = False
        if "retiring" in m and m["retiring"]:
            retiring = True
            retiring_font_begin = "[bold cyan]"
            retiring_font_end = "[/bold cyan]"
        else:
            retiring_font_begin = ""
            retiring_font_end = ""

        table.add_row(f'{retiring_font_begin}{i + 1}{retiring_font_end}',
                      f'{retiring_font_begin}{m["id"]}{retiring_font_end}',
                      f'{retiring_font_begin}[bold {color}]{m["name"]}[/bold {color}]{retiring_font_end}',
                      f'{retiring_font_begin}{unicode_logo}{m["os"]}{retiring_font_end}',
                      f'{retiring_font_begin}[bold {color}]{m["difficultyText"]}[/bold {color}]{retiring_font_end}',
                      f'{retiring_font_begin}{m["stars"]}{retiring_font_end}',
                      f'{retiring_font_begin}{"[bold green]" if m["authUserInUserOwns"] else ""}{format_bool(m["authUserInUserOwns"])}{"[/bold green]" if m["authUserInUserOwns"] else ""}{retiring_font_end}',
                      f'{retiring_font_begin}{"[bold green]" if m["authUserInUserOwns"] else ""}{format_bool(m["authUserInRootOwns"])}{"[/bold green]" if m["authUserInRootOwns"] else ""}{retiring_font_end}',
                      f'{retiring_font_begin}{format_bool(m["retired"])}{f'/{format_bool(True)}' if retiring else ""}{retiring_font_end}',
                      f'{retiring_font_begin}{m["release_date"].strftime("%Y-%m-%d") if m["release_date"] <= datetime.now(tz=timezone.utc) else m["release_date"].strftime("%Y-%m-%d %H:%M:%S UTC")}{retiring_font_end}'
                      )
    return found



def create_machine_list_group_by_retired(machine_info: List[dict]) -> Panel | Group | Table:
    """Create the panel for machine list group by retired/active."""
    assert machine_info is not None

    panels = []
    for machine_type in ["active", "retired", "unreleased"]:
        table = _create_machine_list_table_header()
        filter_type = lambda x: x["retired"] == (machine_type == "retired") and x["release_date"] <= datetime.now(tz=timezone.utc) if machine_type in ["active", "retired"] else x["release_date"] > datetime.now(tz=timezone.utc)
        if _create_machine_list_table_rows(table=table, machine_info=machine_info, filter_type=filter_type):
            panels.append(Panel(table,
                                title=f"[bold yellow]{"Retired" if machine_type == "retired" else "Active" if machine_type == "active" else "Scheduled"}[/bold yellow]",
                                border_style="yellow",
                                title_align="left",
                                expand=True))

    return Group(*panels)


def create_machine_list_group_by_os(machine_info: List[dict]) -> Panel | Group | Table:
    """Create the panel for machine list group by OS."""
    assert machine_info is not None

    os_set: Set[str] = set([x["os"] for x in machine_info])

    panels = []
    for os in os_set:
        table = _create_machine_list_table_header()
        filter_type = lambda x: x["os"] == os
        if _create_machine_list_table_rows(table=table, machine_info=machine_info, filter_type=filter_type):
            panels.append(Panel(table,
                                title=f"[bold yellow]{os}[/bold yellow]",
                                border_style="yellow",
                                title_align="left",
                                expand=True))

    return Group(*panels)