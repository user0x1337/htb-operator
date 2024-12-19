import argparse
from typing import List, Optional

from colorama import Fore, Style
from python_hosts import Hosts, HostsEntry

from command.base import BaseCommand, IS_WINDOWS, IS_ROOT_OR_ADMIN
from htbapi import ActiveMachineInfo


class VhostCommand(BaseCommand):
    hosts_file: Hosts
    vhosts: Optional[str]
    no_machine_hostname: bool

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli, args)
        self.hosts_file: Hosts = Hosts(path=Hosts.determine_hosts_path())
        self.vhosts: Optional[str] = args.subdomain if hasattr(args, "subdomain") else None
        self.no_machine_hostname = args.no_machine_hostname if hasattr(args, "no_machine_hostname") else False

    def add_vhost_to_hosts_file(self, active_machine: ActiveMachineInfo, vhosts: List[str]) -> None:
        """Add vhost to hosts file"""
        htb_hostname = f'{active_machine.name.strip().lower()}.htb'

        # Normalize vhosts, just use lowercase since a domain is not case-sensitive.
        vhosts = list(set([x.lower().strip() for x in vhosts]))

        if self.hosts_file.exists(names=[htb_hostname]):
            host_entry: HostsEntry = next(x for x in self.hosts_file.find_all_matching(name=htb_hostname))

            for vhost in vhosts:
                if not self.no_machine_hostname:
                    vhost = f'{vhost}.{htb_hostname}'

                if vhost not in host_entry.names:
                    host_entry.names.append(vhost)

            host_entry.comment = "Added by HTB-CLI for HackTheBox"

            self._write_hosts_file()
            self.logger.info(f'{Fore.GREEN}Hosts file successfully updated with vhost(s){Style.RESET_ALL}')
        else:
            self.logger.error(f'{Fore.RED}No entry found for hostname "{htb_hostname}". Vhost(s) could not be added.{Style.RESET_ALL}')

    def _write_hosts_file(self):
        """Write hosts file"""
        if IS_ROOT_OR_ADMIN:
            self.hosts_file.write()
        else:
            self.logger.error(f"{Fore.RED}Only {'Administrator' if IS_WINDOWS else 'root'} can write to the hosts file{Style.RESET_ALL}")
            return None

    def add_htb_hostname(self, active_machine: ActiveMachineInfo, htb_hostname: str) -> None:
        """Update hosts file"""
        if self.hosts_file.exists(names=[htb_hostname]):
            host_entry: HostsEntry = next(x for x in self.hosts_file.find_all_matching(name=htb_hostname))
            host_entry.address = active_machine.ip
            host_entry.comment = "Added by HTB-CLI for HackTheBox"
        else:
            host_entry: HostsEntry = HostsEntry(entry_type="ipv4", address=active_machine.ip, names=[htb_hostname],
                                                comment="Added by HTB-CLI for HackTheBox")
            self.hosts_file.add([host_entry])

        self._write_hosts_file()
        self.logger.info(f'{Fore.GREEN}Hosts file successfully updated HTB hostname "{htb_hostname}"{Style.RESET_ALL}')

    def execute(self):
        active_machine: ActiveMachineInfo = self.client.get_active_machine()
        if active_machine is None:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No active machine found{Style.RESET_ALL}')
            return None

        if self.args.vhost == "add" and (self.vhosts is None or len(self.vhosts) == 0):
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No vhosts found{Style.RESET_ALL}')
            return None

        # Only root/admin can write in the hosts file
        self.switch_to_root()

        if self.args.vhost == "add-hostname":
            self.add_htb_hostname(active_machine=active_machine, htb_hostname=f'{active_machine.name.strip().lower()}.htb')
        else:
            vhost_list = [x.strip().lower() for x in self.vhosts.split(",")]
            self.add_vhost_to_hosts_file(active_machine=active_machine, vhosts=vhost_list)
