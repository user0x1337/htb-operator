import argparse
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Optional, List, Tuple

import paramiko
from colorama import Fore, Style
from python_hosts import Hosts

from command.base import BaseCommand, IS_ROOT_OR_ADMIN, IS_WINDOWS
from console import create_panel_active_machine_status, create_machine_list_group_by_retired, \
    create_machine_list_group_by_os, create_machine_info_panel
from htbapi import MachineInfo, ActiveMachineInfo, VpnServerInfo, MachineTopOwns


class MachineCommand(BaseCommand):
    hosts_file: Hosts
    machine_command: Optional[str]
    args_id: Optional[int]
    args_name: Optional[str]
    update_hosts_file: Optional[bool]
    start_vpn: Optional[bool]
    # noinspection PyUnresolvedReferences
    scripts: Optional[str]
    vhost_hostnames: Optional[str]
    vhost_no_machine_hostname: bool
    search_keyword: Optional[str]
    limit_search: Optional[int]
    retired_machines: Optional[bool]
    active_machines: Optional[bool]


    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)

        self.machine_command: Optional[str] = args.machine if hasattr(args, "machine") else None
        self.args_id: Optional[int] = args.id if hasattr(args, "id") else None
        self.args_name: Optional[str] = args.name if hasattr(args, "id") else None
        self.start_vpn = args.start_vpn if hasattr(args, "start_vpn") else False
        self.scripts = args.script if hasattr(args, "script") else None
        self.hosts_file: Hosts = Hosts(path=Hosts.determine_hosts_path())
        self.update_hosts_file = (hasattr(args, "update_hosts_file") and args.update_hosts_file) or (hasattr(args, "clean_hosts_file") and args.clean_hosts_file)
        self.vhost_hostnames = args.vhost_hostname if hasattr(args, "vhost_hostname") else None
        self.vhost_no_machine_hostname = args.vhost_no_machine_hostname if hasattr(args, "vhost_no_machine_hostname") else False
        self.retired_machines = args.retired if hasattr(args, "retired") else None
        self.search_keyword = args.search if hasattr(args, "search") else None
        self.limit_search = args.limit if hasattr(args, "limit") else None
        self.active_machines = args.active if hasattr(args, "active") else None


        # Writing into hosts file needs root/admin privileges
        if self.update_hosts_file or self.start_vpn or (hasattr(args, "stop_vpn") and self.args.stop_vpn):
            self.switch_to_root(callback_execute_after_root_finished=self.try_execute_scripts)


    def check(self) -> bool:
        if not self.machine_command:
            self.logger.error(f"{Fore.RED}No options. Use --help for more information.{Style.RESET_ALL}")
            return False

        if self.args.machine == "info":
            if self.args_id is None and self.args_name is None:
                self.htb_cli.logger.error(
                    f"{Fore.RED}ID or Name must be specified. Use --help for more information.{Style.RESET_ALL}")
                return False

        if self.args.machine == "start":
            if self.args_id is None and self.args_name is None:
                self.htb_cli.logger.error(
                    f"{Fore.RED}ID or Name must be specified. Use --help for more information.{Style.RESET_ALL}")
                return False

            # Check the existence of the script files
            if self.scripts is not None:
                files = self.scripts.split(",")
                failed = False
                for file in files:
                    if not os.path.exists(file):
                        self.logger.error(f"{Fore.RED}File {file} does not exist{Style.RESET_ALL}")
                        failed = True
                    elif not os.path.isfile(file):
                        self.logger.error(f"{Fore.RED}{file} is not a file{Style.RESET_ALL}")
                        failed = True
                if failed:
                    return False

        if self.args.machine == "submit":
            if self.args.user_flag is None and self.args.root_flag is None:
                self.logger.error(f'{Fore.RED}Flag not specified{Style.RESET_ALL}')
                return False
            if self.args.difficulty is None:
                self.logger.error(f'{Fore.RED}Difficulty not specified{Style.RESET_ALL}')
                return False
            if self.args.difficulty < 0 or self.args.difficulty > 10:
                self.logger.error(f'{Fore.RED}Difficulty must be between 0 and 10{Style.RESET_ALL}')
                return False

        if self.args.machine == "ssh-grab":
            if self.args.username is None:
                self.logger.error(f'{Fore.RED}Username not specified{Style.RESET_ALL}')
                return False
            if self.args.password is None:
                self.logger.error(f'{Fore.RED}Password not specified{Style.RESET_ALL}')
                return False
            if self.args.host is None:
                self.logger.error(f'{Fore.RED}Host not specified{Style.RESET_ALL}')
                return False
            if self.args.difficulty is None:
                self.logger.error(f'{Fore.RED}Difficulty not specified{Style.RESET_ALL}')
                return False
            if self.args.difficulty < 0 or self.args.difficulty > 10:
                self.logger.error(f'{Fore.RED}Difficulty must be between 0 and 10{Style.RESET_ALL}')
                return False

        return True

    def write_hosts_file(self):
        """Write hosts file"""
        if IS_ROOT_OR_ADMIN:
            self.hosts_file.write()
            self.logger.info(f"{Fore.GREEN}Updated hosts file {self.hosts_file.path}{Style.RESET_ALL}")
        else:
            self.logger.error(f"{Fore.RED}Only {'Administrator' if IS_WINDOWS else 'root'} can write to the hosts file{Style.RESET_ALL}")
            return None

    def remove_from_hosts(self, old_ip: str):
        """Remove ip from hosts file"""
        if self.hosts_file.exists(address=old_ip):
            self.hosts_file.remove_all_matching(address=old_ip)
            self.write_hosts_file()

    def update_hosts(self, active_machine: ActiveMachineInfo) -> str:
        """Update the hosts file with the htb hostname"""
        from command import VhostCommand

        htb_hostname = f'{active_machine.name.strip().lower()}.htb'
        if not self.update_hosts_file:
            return htb_hostname

        vhost_command: VhostCommand = VhostCommand(htb_cli=self.htb_cli, args=self.args)
        vhost_command.add_htb_hostname(active_machine=active_machine, htb_hostname=htb_hostname)

        return htb_hostname

    def execute_script(self, script:str) -> None:
        self.logger.info(f'{Fore.GREEN}Executing script: {script}{Style.RESET_ALL}')

        try:
            if IS_WINDOWS:
                pwsh = shutil.which("pwsh") if shutil.which("pwsh") else shutil.which("powershell")
                subprocess.run([pwsh, "-ep", "bypass"] + [script],
                               stdout=sys.stdout,
                               stderr=sys.stderr,
                               stdin=sys.stdin,
                               env=os.environ.copy(),
                               text=True)
            else:
                subprocess.run([shutil.which("bash")] + [script],
                               stdout=sys.stdout,
                               stderr=sys.stderr,
                               stdin=sys.stdin,
                               env=os.environ.copy(),
                               text=True)
        except Exception as e:
            self.logger.error(f'Error executing script: {e}{Style.RESET_ALL}')
            return None


    def _execute_and_wait_for_ip_assigning(self, exec_machine_command: any, machine_name: str) -> None:
        from command import VpnCommand

        animation_thread = None
        active_machine : Optional[ActiveMachineInfo] = None
        try:
            res, msg = exec_machine_command()
            if res:
                self.logger.info(f'{Fore.GREEN}Machine "{machine_name}": {msg}{Style.RESET_ALL}')
                self.stop_animation = threading.Event()

                time.sleep(3)
                active_machine = self.client.get_active_machine()

                if self.start_vpn and active_machine is not None:
                    old_id = self.args.id
                    self.args.id = active_machine.vpn_server_id
                    vpn_command = VpnCommand(htb_cli=self.htb_cli, args=self.args)
                    vpn_command.start_vpn()
                    self.args.id = old_id

                animation_thread = threading.Thread(target=self.animate_spinner, args=("Waiting... IP is being assigned.", f'Machine "{machine_name}"'))
                animation_thread.start()

                # Spawning finished?
                while active_machine is not None and active_machine.isSpawning:
                    time.sleep(5)
                    active_machine = self.client.get_active_machine()

                if active_machine is None:
                    self.logger.error(f'{Fore.RED} Anything went wrong... No active machine could be found.{Style.RESET_ALL}')
                    return None
        finally:
            self.stop_animation.set()
            if animation_thread is not None:
                animation_thread.join()

        if not res:
            self.logger.error(f'\r{Fore.RED}[-] Machine "{machine_name}": {msg.ljust(60)}{Style.RESET_ALL}')
        elif active_machine is not None and active_machine.ip is not None:
            self.logger.info(f'\r{Fore.GREEN}[+] Machine "{machine_name}": IP successfully assigned.{Style.RESET_ALL}'.ljust(80))
            htb_hostname = self.update_hosts(active_machine)
            os.environ["HTB_MACHINE_HOSTNAME"] = htb_hostname

            # Adding vhosts if indicated
            if self.vhost_hostnames is not None and len(self.vhost_hostnames) > 0:
                from command import VhostCommand
                self.args.subdomain =  self.vhost_hostnames
                self.args.no_machine_hostname = self.vhost_no_machine_hostname
                self.args.vhost = "add"
                vhost_command = VhostCommand(htb_cli=self.htb_cli, args=self.args)
                vhost_command.execute()

            # refresh host file because it might be modified
            self.hosts_file: Hosts = Hosts(path=Hosts.determine_hosts_path())

            # Show machine status
            self.status_machine()


    def stop_machine(self) -> None:
        """Stops the active machine"""
        from command import VpnCommand

        vpn_command = VpnCommand(htb_cli=self.htb_cli, args=self.args)
        active_machine: ActiveMachineInfo = self.client.get_active_machine()
        if active_machine is None or active_machine.id is None:
            return None

        machine: MachineInfo = self.client.get_machine(machine_id_or_name=active_machine.id)
        old_ip: str = active_machine.ip
        self.stop_animation = threading.Event()
        animation_thread = threading.Thread(target=self.animate_spinner, args=(f"Machine is terminating...", f'Machine "{machine.name}"'))
        try:
            animation_thread.start()
            res, msg = machine.stop()

            while res and active_machine is not None:
                time.sleep(5)
                active_machine = self.client.get_active_machine()

            print(f'\r{Fore.GREEN}Machine "{machine.name}": {msg.ljust(80)}{Style.RESET_ALL}')
        finally:
            self.stop_animation.set()
            animation_thread.join()

        if self.update_hosts_file:
            self.remove_from_hosts(old_ip=old_ip)

        if self.args.stop_vpn:
            vpn_command.stop_vpn()

    def _check_or_wait_for_release_date(self, machine:MachineInfo) -> bool:
        time_left = machine.release_date - datetime.now().astimezone(timezone.utc)
        if time_left.total_seconds() <= 0:
            return True

        if not self.args.wait_for_release:
            self.logger.error(f'Machine has not been release, yet. Release date: {machine.release_date.isoformat()}')
            return False

        self.logger.warning(f'{Fore.LIGHTYELLOW_EX}Machine has not been released, yet. Release date: {machine.release_date.strftime("%Y-%m-%d %H:%M:%S %Z")}. Waiting for release date/time to continue...{Style.RESET_ALL}')
        while int(time_left.total_seconds()) > 0:
            time_left = machine.release_date - datetime.now().astimezone(timezone.utc)

            # For output
            dummy_date = datetime(1, 1, 1) + time_left
            print(
                f'\r{Fore.CYAN}{dummy_date.strftime(f"{time_left.days} Days %H:%M:%S")} hours left before spawning the machine "{machine.name}"{Style.RESET_ALL}',
                end="", flush=True)
            time.sleep(1)
        else:
            print(f'\r{" ".ljust(120)}{Style.RESET_ALL}', flush=True)

        return True



    def status_machine(self):
        """Status of the active machine"""
        vpn_servers: dict[int, VpnServerInfo] = self.client.get_all_vpn_server(products=["labs", "starting_point", "release_arena"])
        active_machine: ActiveMachineInfo = self.client.get_active_machine()
        if active_machine is None:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX} No active machines{Style.RESET_ALL}')
            return None
        machine: MachineInfo = self.client.get_machine(machine_id_or_name=active_machine.id)

        vpn_server: Optional[VpnServerInfo] = None
        if active_machine.vpn_server_id is not None and active_machine.vpn_server_id in vpn_servers.keys():
            vpn_server: Optional[VpnServerInfo] = vpn_servers.get(active_machine.vpn_server_id)

        active_dict = active_machine.to_dict()
        active_dict["info_status"] = "-" if machine.info_status is None else machine.info_status
        active_dict["retired"] = machine.retired
        active_dict["points"] = machine.points
        active_dict["user_owned"] = machine.authUserInUserOwns
        active_dict["root_owned"] = machine.authUserInRootOwns
        active_dict["num_solved"] = machine.root_owns_count
        active_dict["difficulty"] = machine.difficultyText
        active_dict["os"] = machine.os
        active_dict["vpn_server"] = "-" if vpn_server is None else vpn_server.name
        active_dict["num_players"] = "-" if machine.machine_play_info is None else machine.machine_play_info.active_player_count
        active_dict["hosts_file_name"] = "-" if not self.hosts_file.exists(address=active_machine.ip) else "\n".join(self.hosts_file.find_all_matching(address=active_machine.ip)[0].names)
        self.console.print(create_panel_active_machine_status(active_machine=active_dict))

    def start_machine(self):
        machine: MachineInfo = self.htb_cli.client.get_machine(machine_id_or_name=self.args_id if self.args_id else self.args_name)
        if machine is None:
            self.logger.error(
                f'{Fore.RED} Machine not found for id/name "{self.args_id if self.args_id else self.args_name}"{Style.RESET_ALL}')
            return None

        active_machine: ActiveMachineInfo = self.client.get_active_machine()
        if active_machine is None or active_machine.id != machine.id:
            if active_machine is not None and active_machine.id != machine.id:
                start_new_maschine: bool = (input(
                    f'{Fore.LIGHTYELLOW_EX}The machine "{active_machine.name}" (ID: {active_machine.id}) already spawned. Do you want to stop the machine to start the machine "{machine.name}" (y/N): {Style.RESET_ALL}').strip().lower() == "y")
                if not start_new_maschine:
                    return None
                else:
                    self.args.stop_vpn = active_machine.vpn_server_id not in [x.server_id for x in self.client.get_active_connections()]
                    self.stop_machine()

            if not self._check_or_wait_for_release_date(machine=machine):
                return None

            self._execute_and_wait_for_ip_assigning(exec_machine_command=machine.start, machine_name=machine.name)
        else:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}Machine "{machine.name}" already spawned!{Style.RESET_ALL}')
            from command import VpnCommand

            vpn_command = VpnCommand(htb_cli=self.htb_cli, args=self.args)
            if self.start_vpn and active_machine is not None:
                vpn_command.vpn_id = active_machine.vpn_server_id
                vpn_command.start_vpn()


    def try_execute_scripts(self):
        """Try to execute the custom user scripts"""
        if self.scripts is None or len(self.scripts) == 0:
            return None

        active_machine: ActiveMachineInfo = self.client.get_active_machine()
        machine: Optional[MachineInfo] = None
        if active_machine is not None:
            machine: Optional[MachineInfo] = self.htb_cli.client.get_machine(machine_id_or_name=active_machine.id)

        os.environ["HTB_MACHINE_IP"] = active_machine.ip if active_machine is not None else ""
        os.environ["HTB_MACHINE_NAME"] = active_machine.name if active_machine is not None else ""
        os.environ["HTB_MACHINE_OS"] = machine.os if machine is not None else ""
        os.environ["HTB_MACHINE_DIFFICULTY"] = machine.difficultyText if machine is not None else ""
        os.environ["HTB_MACHINE_INFO"] = machine.info_status if machine is not None and machine.info_status is not None else ""
        os.environ["HTB_MACHINE_HOSTNAME"] = f'{active_machine.name.strip().lower()}.htb' if active_machine is not None else ""

        self.logger.warning(f'{Fore.LIGHTYELLOW_EX}Running script as user "{os.getlogin()}"{Style.RESET_ALL}')
        script_file_list = self.scripts.split(",")
        for script in script_file_list:
            self.execute_script(script=script)
            self.logger.info(f'{Fore.GREEN}Script execution finished{Style.RESET_ALL}')


    def list(self):
        if not self.check():
            return False

        os_filter = []
        if self.args.filter_win:
            os_filter.append("windows")
        if self.args.filter_linux:
            os_filter.append("linux")
        if self.args.filter_freebsd:
            os_filter.append("freebsd")
        if self.args.filter_openbsd:
            os_filter.append("openbsd")
        if self.args.filter_other_os:
            os_filter.append("others")

        scheduled_machines: List[Tuple[MachineInfo, MachineInfo]] = self.client.get_unreleased_machines()
        retiring_machines: List[MachineInfo] = [x[1] for x in scheduled_machines]

        machines_result: List[MachineInfo] = []
        # No filter set? -> Get all machines (both active and retired ones)
        if self.retired_machines is None and self.active_machines is None or (not self.retired_machines and not self.active_machines):
            machines_result += self.client.get_machine_list(retired=False, keyword=self.search_keyword, limit=self.limit_search, os_filter=os_filter)
            machines_result += self.client.get_machine_list(retired=True, keyword=self.search_keyword, limit=self.limit_search, os_filter=os_filter)
            machines_result += [x[0] for x in scheduled_machines]

        elif self.retired_machines:
            machines_result += self.client.get_machine_list(retired=True, keyword=self.search_keyword, limit=self.limit_search, os_filter=os_filter)
        elif self.active_machines:
            machines_result += self.client.get_machine_list(retired=False, keyword=self.search_keyword, limit=self.limit_search, os_filter=os_filter)

        if len(machines_result) == 0:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No machines found{Style.RESET_ALL}')
            return None

        if self.args.group_by_os:
            self.console.print(create_machine_list_group_by_os(machine_info=[x.to_dict() for x in machines_result]))
        else:
            maschine_dict_list = []
            for machine in machines_result:
                machine_dict = machine.to_dict()
                if machine in retiring_machines:
                    machine_dict["retiring"] = True
                maschine_dict_list.append(machine_dict)

            self.console.print(create_machine_list_group_by_retired(machine_info=maschine_dict_list))


    def reset_machine(self):
        """Resets the active machine"""
        active_machine: ActiveMachineInfo = self.client.get_active_machine()
        if active_machine is None:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No active machines{Style.RESET_ALL}')
            return None

        machine: MachineInfo = self.client.get_machine(machine_id_or_name=active_machine.id)
        self._execute_and_wait_for_ip_assigning(exec_machine_command=machine.reset, machine_name=machine.name)


    def submit_flag(self):
        """Submits a flag to the machine"""

        def print_status():
            if status:
                self.logger.info(f'{Fore.GREEN}{msg}{Style.RESET_ALL}')
            else:
                self.logger.error(f'{Fore.RED}Error: {msg}{Style.RESET_ALL}')

        if not self.check():
            return None

        active_machine: ActiveMachineInfo = self.client.get_active_machine()
        if active_machine is None:
            self.logger.error(f'{Fore.RED}No a active machine{Style.RESET_ALL}')
            return None

        if self.args.user_flag:
            status, msg = active_machine.submit(flag=self.args.user_flag)
            print_status()
            status, msg = active_machine.rate_flag(flag_type="user", difficulty=self.args.difficulty)
            print_status()

        if self.args.root_flag:
            status, msg = active_machine.submit(flag=self.args.root_flag)
            print_status()
            status, msg = active_machine.rate_flag(flag_type="root", difficulty=self.args.difficulty)
            print_status()

    def grab_flag_via_ssh(self):
        """Try to grab the flag via SSH"""
        if not self.check():
            return None

        self.logger.info(f'{Fore.GREEN}Initialize ssh-connection{Style.RESET_ALL}')
        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.args.host,
                           username=self.args.username,
                           password=self.args.password)
            self.logger.info(f'{Fore.GREEN}SSH-Connection to {self.args.host} with user {self.args.username} established{Style.RESET_ALL}')

            if "root" == self.args.username.strip():
                stdin, stdout, stderr = client.exec_command(f'cat /{self.args.username.strip()}/root.txt')
                output = stdout.read().decode().strip()
            else:
                stdin, stdout, stderr = client.exec_command(f'cat /home/{self.args.username.strip()}/user.txt')
                output = stdout.read().decode().strip()

        if "No such file".lower() in output.lower() or len(output) == 0:
            self.logger.error(f'{Fore.RED}No flag found{Style.RESET_ALL}')
        else:
            self.logger.info(f'{Fore.GREEN}Flag "{output}" found for user {self.args.username}{Style.RESET_ALL}')
            if "root" == self.args.username:
                self.args.root_flag = output
                self.args.user_flag = None
            else:
                self.args.root_flag = None
                self.args.user_flag = output


            if (self.args.user_flag and len(self.args.user_flag)) or (self.args.root_flag and len(self.args.root_flag) > 0):
                self.logger.info(f'{Fore.GREEN}Start submitting the flag{Style.RESET_ALL}')
                self.submit_flag()
            else:
                self.logger.warning(f'{Fore.LIGHTYELLOW_EX}Flag is empty. No submission.{Style.RESET_ALL}')

    def extend_machine(self):
        """Extend the time of a machine"""
        active_machine: ActiveMachineInfo = self.client.get_active_machine()
        if active_machine is None:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No active machines{Style.RESET_ALL}')
            return None

        machine: MachineInfo = self.client.get_machine(machine_id_or_name=active_machine.id)
        res, msg = machine.extend()
        if res:
            self.logger.info(f'{Fore.GREEN}Machine "{machine.name}": {msg}{Style.RESET_ALL}')
        else:
            self.logger.error(f'{Fore.RED}Machine "{machine.name}": {msg}{Style.RESET_ALL}')


    def print_info(self):
        """Print the machine info"""
        machine: MachineInfo = self.client.get_machine(machine_id_or_name=self.args_id if self.args_id else self.args_name)
        self.console.print(create_machine_info_panel(machine_info=machine.to_dict(details=True)))

    def execute(self):
        if not self.check():
            return None

        if self.args.machine == "start":
            self.start_machine()
        elif self.machine_command == "status":
           self.status_machine()
        elif self.machine_command == "stop":
            self.stop_machine()
        elif self.machine_command == "reset":
            self.reset_machine()
        elif self.machine_command == "extend":
            self.extend_machine()
        elif self.machine_command == "submit":
            self.submit_flag()
        elif self.machine_command == "ssh-grab":
            self.grab_flag_via_ssh()
        elif self.machine_command == "list":
            self.list()
        elif self.machine_command == "info":
            self.print_info()
        else:
            self.logger.error(f'{Fore.RED}Unknown command "{self.machine_command}{Style.RESET_ALL}')
            return None
