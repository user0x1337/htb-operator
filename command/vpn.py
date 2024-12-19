import argparse
import os
import re
import signal
import socket
import subprocess
import sys
from typing import Optional, List

import psutil
from colorama import Fore, Style
from tqdm import tqdm

from command.base import BaseCommand, IS_WINDOWS
from console import create_table_active_vpn_connections, create_vpn_list_table, create_benchmark_table
from htbapi import VpnServerInfo, AccessibleVpnServer, RequestException, CannotSwitchWithActive, \
    VpnException, BaseVpnServer, ActiveMachineInfo


class VpnCommand(BaseCommand):
    vpn_id: Optional[int]
    target_path: Optional[str]
    tcp: bool
    accessible_vpn_servers: dict[int, AccessibleVpnServer]
    regex_ping: str

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli, args)

        self.vpn_command: Optional[str] = args.vpn if hasattr(args, "vpn") else None
        self.vpn_id = None if not hasattr(args, "id") else args.id
        self.tcp = False if not hasattr(args, "tcp") else args.tcp
        self.target_interface = "tun_htb" if not hasattr(args, "interface") else args.interface
        self.target_path = None if not hasattr(args, "path") else args.path
        self.accessible_vpn_servers = self.client.get_accessible_vpn_server()
        self.regex_ping = r"min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms"

        # VPN operations needs root/admin privileges
        if self.vpn_command in ["start", "stop"]:
            self.switch_to_root()

    def check(self) -> bool:
        """Checks"""
        if IS_WINDOWS:
            self.logger.error(f'{Fore.RED}VPN feature is not supported on Windows. Please start it manually.{Style.RESET_ALL}')
            return False

        return True

    def read_vpn_file(self, vpn: VpnServerInfo):
        """Get the content of the downloaded VPN file"""
        path: Optional[str] = None
        try:
            path = vpn.download()
            with open(path, "r") as f:
                return f.read()
        except RequestException as e:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}VPN "{vpn.name}"({vpn.id}): {e.args[0]["message"]}{Style.RESET_ALL}')
            return None
        finally:
            if path is not None:
                os.remove(path)

    def ping_hostname(self, hostname: str, count: int=3) -> float:
        """Ping the hostname"""
        try:
            p = subprocess.run(
                ["ping", "-c", f'{count}', hostname],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True)
            output = p.stdout
            match = re.search(self.regex_ping, output)
            if match:
                min_latency, avg_latency, max_latency, mdev = match.groups()
                return float(avg_latency)
            else:
                self.logger.error(f"{Fore.RED}Error: Latency could not be parsed: {output}{Style.RESET_ALL}")
                return 99999999.99
        except subprocess.CalledProcessError as e:
            self.logger.error(f"{Fore.RED}Ping failed: {e.stderr}{Style.RESET_ALL}")
            return 99999999.99
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            return 99999999.99

    def _get_products(self):
        """Get the products"""
        products: List[str] = []
        if self.args.starting_point:
            products.append("starting_point")
        if self.args.endgames:
            products.append("endgames")
        if self.args.fortresses:
            products.append("fortresses")
        if self.args.release_arena:
            products.append("release_arena")
        if self.args.prolabs:
            products.append("prolab")
        if self.args.labs:
            products.append("labs")

        if len(products) == 0:
            products = ["labs", "starting_point", "fortresses", "release_arena", "endgames", "prolab"]

        return products

    def do_benchmark(self):
        """Performing benchmark"""
        self.logger.info(f'{Fore.GREEN}Starting benchmark{Style.RESET_ALL}')
        vpn_servers: dict[int, VpnServerInfo] = self.client.get_all_vpn_server(products=self._get_products(), vpn_location=self.args.location)

        if self.args.only_accessible:
            vpn_servers = {k:v for k,v in vpn_servers.items() if k in self.accessible_vpn_servers.keys()}

        # The "backup". Need it later for restoring old state.
        accessible_vpn_servers: dict[int, AccessibleVpnServer] = self.client.get_accessible_vpn_server()

        result: dict[int, Optional[dict]] = dict()
        try:
            pbar_servers = tqdm(vpn_servers.values())
            for vpn in pbar_servers:
                pbar_servers.set_description(f'Testing "{vpn.name}" (Location: {vpn.location})')
                data = self.read_vpn_file(vpn=vpn)
                if data is None:
                    continue

                remote_line = next(x for x in data.split("\n") if x.startswith("remote"))
                hostname = remote_line.split()[1]
                vpn_server: dict = vpn_servers[vpn.id].to_dict()
                vpn_server["latency"] = self.ping_hostname(hostname, count=2)
                vpn_server["hostname"] = hostname
                vpn_server["is_assigned"] = bool(vpn.id in accessible_vpn_servers.keys())
                result[vpn.id] = vpn_server
        except KeyboardInterrupt:
            pass

        result = {k: v for k, v in sorted(result.items(), key=lambda item: (item[1]["latency"] is None, item[1]["latency"]))}
        for accessible_vpn_server_id in accessible_vpn_servers.keys():
            if accessible_vpn_server_id in vpn_servers.keys():
                vpn = vpn_servers[accessible_vpn_server_id]
                try:
                    vpn.switch()
                except KeyboardInterrupt:
                    break

        self.logger.info(f'{Fore.GREEN}Benchmark done{Style.RESET_ALL}')
        self.console.print(create_benchmark_table(vpn_benchmark_results=[x for x in result.values()]))

    def get_interface_for_ip(self, ip_address: str):
        """Gets the interface for a given IP"""
        try:
            interfaces: dict = psutil.net_if_addrs()

            for interface, addresses in interfaces.items():
                for address in addresses:
                    if address.family == socket.AF_INET and address.address == ip_address:
                        return interface

            return None
        except Exception as e:
            self.logger.error(f"Error during finding the interface: {e}")
            return None

    def get_next_free_tun_interface(self):
        """Find a free (unused) tun interface that can be used"""
        if IS_WINDOWS:
            raise NotImplementedError

        try:
            result = subprocess.run(['ip', 'link'],
                                    stdout=subprocess.PIPE,
                                    text=True)

            interfaces = result.stdout.splitlines()
            used_tuns = set()
            for line in interfaces:
                if self.target_interface not in line:
                    continue

                parts = line.split(":")
                if len(parts) <= 1:
                    continue

                interface_name = parts[1].strip()
                if interface_name.startswith(self.target_interface):
                    used_tuns.add(interface_name)

            if len(used_tuns) == 0:
                return self.target_interface

            return f"{self.target_interface}{next(i for i in range(0, 255) if f'{self.target_interface}{i}' not in used_tuns)}"
        except Exception as e:
            self.logger.error(f'Error during finding a free tun interface: {e}')
            return None

    def do_download(self):
        """Download the VPN server ovpn file"""
        try:
            res = VpnServerInfo.download_ovpn_file(vpn_id=self.vpn_id, _client=self.client, tcp=self.tcp, path=self.target_path)
            if res:
                self.logger.info(f'{Fore.GREEN}OpenVPN file successfully download in {res}{Style.RESET_ALL}')
        except CannotSwitchWithActive as e:
            self.logger.error(f'{Fore.RED}Cannot download OpenVPN Configuration: {e}{Style.RESET_ALL}')
        except VpnException as e:
            self.logger.error(f'{Fore.RED}OpenVPN Error: {e}{Style.RESET_ALL}')
        except RequestException as e:
            self.logger.error(f'{Fore.RED}Error: {e.args[0]["message"]}{Style.RESET_ALL}')

    def do_switch(self) -> bool:
        """Switching VPN-Server"""
        try:
            vpn_server: BaseVpnServer = VpnServerInfo.switch_vpn_server(vpn_id=self.vpn_id, _client=self.client)
            if vpn_server:
                self.logger.info(f'{Fore.GREEN}VPN-Server to "{vpn_server.name}" successfully switched (# Clients: {vpn_server.current_clients}){Style.RESET_ALL}')
                return True
            self.logger.error(f'{Fore.RED}Could not switch VPN Server.{Style.RESET_ALL}')
        except CannotSwitchWithActive as e:
            self.logger.error(f'{Fore.RED}Cannot switch VPN Server: {e}{Style.RESET_ALL}')
        except VpnException as e:
            self.logger.error(f'{Fore.RED}VPN Error: {e}{Style.RESET_ALL}')
        except RequestException as e:
            self.logger.error(f'{Fore.RED}Error: {e.args[0]["message"]}{Style.RESET_ALL}')

        return False


    def stop_vpn(self):
        """Stop all active HTB-VPN-Server"""
        if IS_WINDOWS:
            raise NotImplementedError

        p = subprocess.run(['pgrep', '-fa', 'openvpn'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           text=True)

        lines = p.stdout.splitlines()
        if lines is None or len(lines) == 0:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No running OpenVPN connections found{Style.RESET_ALL}')
            return None

        for line in lines:
            elements = line.split(" ")
            process_id = int(elements[0])

            configparser_filepath: Optional[str] = None
            for index, value in enumerate(elements):
                if value == "--config" and index < len(elements) - 1:
                    configparser_filepath = elements[index + 1].strip()
                    break
                elif value.strip().endswith(".ovpn"):
                    configparser_filepath = value.strip()

            if configparser_filepath is None:
                continue

            with open(configparser_filepath) as f:
                content_lines = f.readlines()

            for content_line in content_lines:
                if "remote" in content_line and "hackthebox." in content_line:
                    self.logger.info(f'{Fore.GREEN}Found HTB OpenVPN connection (Process-ID: {process_id}). Send signal SIGTERM to kill the process{Style.RESET_ALL}')
                    os.kill(process_id, signal.SIGTERM)

        self.logger.info(f'{Fore.GREEN}Stopped all found HTB OpenVPN connections{Style.RESET_ALL}')


    def start_vpn(self):
        """Start the VPN connection."""
        if self.vpn_id is not None and self.vpn_id not in self.accessible_vpn_servers.keys():
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}VPN-Server with VPN-ID {self.vpn_id} is not found or accessible.{Style.RESET_ALL}\n')
            try:
                resp: Optional[str] = input(f'{Fore.LIGHTYELLOW_EX}Try to switch the accessible VPN-Servers? (y/N): {Style.RESET_ALL}')
            except KeyboardInterrupt:
                return None
            if resp is None or len(resp.strip()) == 0 or resp.strip().lower() != "y":
                return None
            elif not self.do_switch():
                return None

            self.accessible_vpn_servers = self.client.get_accessible_vpn_server()

        if self.vpn_id is not None:
            vpn_server = self.accessible_vpn_servers[self.vpn_id]
        else:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No VPN-Id stated. Try to determine the vpn server based on the active running machine{Style.RESET_ALL}')
            active_machine: ActiveMachineInfo = self.client.get_active_machine()
            if active_machine is not None:
                vpn_server = self.accessible_vpn_servers[active_machine.vpn_server_id]
                self.logger.info(f'{Fore.GREEN}VPN-Server could be determined{Style.RESET_ALL}')
            else:
                self.logger.error(f'{Fore.RED}No VPN-ID stated and no active running machine found{Style.RESET_ALL}')
                return None
        try:
            for conn in self.client.get_active_connections():
                intf: Optional[str] = self.get_interface_for_ip(conn.connection_ipv4)
                if intf is not None:
                    self.logger.warning(
                        f'{Fore.LIGHTYELLOW_EX}VPN Connection already established on interface "{intf}" with IPv4 "{conn.connection_ipv4}" / IPv6 "{conn.connection_ipv6}"{Style.RESET_ALL}')
                    return None

            available_tun = self.get_next_free_tun_interface()
            process = subprocess.Popen(["openvpn",
                                        "--config", vpn_server.download(path=self.target_path, tcp=self.tcp),
                                        "--dev", available_tun],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL,
                                       env=os.environ.copy(),
                                       start_new_session=True,
                                       text=True)

            for line in process.stdout:
                if "Peer Connection Initiated" in line:
                    self.logger.info(f'{Fore.GREEN}Establishing VPN connection...{Style.RESET_ALL}')
                elif "net_addr_v4_add" in line or "net_addr_v6_add" in line:
                    lines = line.split(" ")
                    if len(lines) > 3:
                        self.logger.info(
                            f'{Fore.GREEN}IP{"v4" if "net_addr_v4_add" in line else "v6"}: {lines[3]}{Style.RESET_ALL}')
                elif "Initialization Sequence Completed" in line:
                    self.logger.info(
                        f'{Fore.GREEN}OpenVPN started for server "{vpn_server.name}" on interface {available_tun} with process id "{process.pid}".{Style.RESET_ALL}')
                    break
                elif "ERROR" in line:
                    self.logger.error(f'{Fore.RED}{line.strip()}{Style.RESET_ALL}')
                elif "Exiting due to fatal error" in line:
                    self.logger.error(f'{Fore.RED}{line.strip()}{Style.RESET_ALL}')
                    break
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


    def print_vpn_servers(self):
        """Print the VPN servers."""
        vpn_servers: dict[int, VpnServerInfo] = self.client.get_all_vpn_server(products=self._get_products())

        if self.args.only_accessible:
            vpn_servers = {k:v for k,v in vpn_servers.items() if k in self.accessible_vpn_servers.keys()}

        if self.args.location is not None and len(self.args.location) > 0:
            vpn_servers = {k: v for k, v in vpn_servers.items() if v.location.casefold() == self.args.location.casefold()}

        if vpn_servers is None or len(vpn_servers.keys()) == 0:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No VPN servers found{Style.RESET_ALL}')
            return None

        self.console.print(create_vpn_list_table(vpn_servers=[v.to_dict() for v in vpn_servers.values()]))
        if self.args.total_clients:
            total_clients = sum(x.current_clients for x in vpn_servers.values())
            self.logger.info(f'{Fore.GREEN}Total current connected clients: {total_clients}{Style.RESET_ALL}')


    def print_connection_status(self):
        """Print the VPN connection status."""
        conns = []
        for x in self.client.get_active_connections():
            conns_dict = x.to_dict()

            # current client is not recorded inside the active connections API but in the accessible vpn servers API
            conns_dict["current_clients"] = self.accessible_vpn_servers[x.server_id].current_clients
            conns_dict["interface"] = self.get_interface_for_ip(x.connection_ipv4)
            conns.append(conns_dict)
        if len(conns) == 0:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No active connections{Style.RESET_ALL}')
        else:
            self.console.print(create_table_active_vpn_connections(vpn_connections=conns))

    def execute(self):
        """Execute the command"""
        if not self.check():
            return None
        elif self.vpn_command == "start":
            self.start_vpn()
        elif self.vpn_command == "status":
            self.print_connection_status()
        elif self.vpn_command == "list":
            self.print_vpn_servers()
        elif self.vpn_command == "benchmark":
            self.do_benchmark()
        elif self.vpn_command == "stop":
            self.stop_vpn()
        elif self.vpn_command == "switch":
            self.do_switch()
        elif self.vpn_command == "download":
            self.do_download()
