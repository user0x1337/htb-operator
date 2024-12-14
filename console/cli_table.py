from typing import List

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


def create_season_list_table(seasons: list) -> Table:
    table = Table(title="Seasons", show_lines=True)
    table.add_column(header="#", style="cyan", justify="left")
    table.add_column(header="ID", style="cyan", justify="left")
    table.add_column(header="Name", style="cyan", justify="left")
    table.add_column(header="Start date", style="cyan", justify="left")
    table.add_column(header="End date", style="cyan", justify="left")
    table.add_column(header="State", style="cyan", justify="left")
    table.add_column(header="Active?", style="cyan", justify="left")

    for i, res in enumerate(seasons):
        table.add_row(f'{i + 1}',
                      f'{res["id"]}',
                      f'{res["name"]}',
                      f'{res["start_date"].strftime("%Y-%m-%d")}',
                      f'{"-" if res["end_date"] is None else res["end_date"].strftime("%Y-%m-%d")}',
                      f'{res["state"]}',
                      f'{format_bool(res["active"])}')
    return table

def create_benchmark_table(vpn_benchmark_results: list) -> Table:
    """Create benchmark table"""
    table = Table(title="Result", show_lines=True)
    table.add_column(header="#", style="cyan", justify="left")
    table.add_column(header="Latency [ms]", style="cyan", justify="left")
    table.add_column(header="VPN-ID", style="cyan", justify="left")
    table.add_column(header="Hostname", style="cyan", justify="left")
    table.add_column(header="Product", style="cyan", justify="left")
    table.add_column(header="Servername", style="cyan", justify="left")
    table.add_column(header="Location", style="cyan", justify="left")
    table.add_column(header="# Clients", style="cyan", justify="left")
    table.add_column(header="Assigned?", style="cyan", justify="left")

    for i, res in enumerate(vpn_benchmark_results):
        table.add_row(f'{i + 1}',
                      f'{res["latency"]}',
                      f'{res["id"]}',
                      f'{res["hostname"]}',
                      f'{res["product"]}',
                      f'{res["name"]}',
                      f'{res["location"]}',
                      f'{res["current_clients"]}',
                      f'{format_bool(res["is_assigned"])}')
    return table

def create_vpn_list_table(vpn_servers: list[dict]) -> Table:
    assert vpn_servers is not None
    vpn_servers = sorted(vpn_servers, key=lambda x: (x['product'], x['location'], x['name']))

    table = Table(title="VPN-Server", show_lines=True)
    table.add_column(header="#", style="cyan", justify="left")
    table.add_column(header="Product", style="cyan", justify="left")
    table.add_column(header="Location", style="cyan", justify="left")
    table.add_column(header="Server-ID", style="cyan", justify="left")
    table.add_column(header="Name", style="cyan", justify="left")
    table.add_column(header="Assigned?", style="cyan", justify="left")
    table.add_column(header="# Clients", style="cyan", justify="left")
    table.add_column(header="Full?", style="cyan", justify="left")

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
    return table

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


def create_table_challenge_list(challenge_list: List[dict], category_dict: dict) -> Table:
    table = Table(title="Challenges", show_lines=True)
    table.add_column(header="ID", style="cyan", justify="left")
    table.add_column(header="Name", style="cyan", justify="left")
    table.add_column(header="Retired", style="cyan", justify="left")
    table.add_column(header="Difficulty", style="cyan", justify="left")
    table.add_column(header="Avg Difficulty", style="cyan", justify="left")
    table.add_column(header="Points", style="cyan", justify="left")
    table.add_column(header="Solved", style="cyan", justify="left")
    table.add_column(header="Release Date", style="cyan", justify="left")
    table.add_column(header="Category", style="cyan", justify="left")
    table.add_column(header="Rating", style="cyan", justify="left")
    table.add_column(header="TODO", style="cyan", justify="left")

    for c in challenge_list:
        table.add_row(str(c["id"]),
                      c["name"],
                      format_bool(c["retired"]),
                      c["difficulty"],
                      f"{c["avg_difficulty"]}",
                      f"{c["points"]}",
                      format_bool(c["solved"]),
                      f"{c["release_date"].strftime('%Y-%m-%d')}",
                      category_dict[c["category_id"]],
                      f"{c["rating"]}",
                      format_bool(c["isTodo"]))

    return table