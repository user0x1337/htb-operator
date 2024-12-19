import argparse
import os
import shutil
import subprocess
import sys
from typing import Optional

from colorama import Fore, Style

from command.base import BaseCommand, IS_WINDOWS
from console import create_pwnbox_panel
from htbapi import PwnboxStatus, NoPwnBoxActiveException


class PwnBoxCommand(BaseCommand):
    pwnbox_command: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli, args)
        self.pwnbox_command = args.pwnbox if hasattr(args, "pwnbox") else None

    def check(self, pwnbox_status):
        """Check some conditions"""
        if self.pwnbox_command == "ssh":
            if pwnbox_status is None:
                return False

            # check for sshpass
            if shutil.which("sshpass") is None:
                self.logger.error(f'{Fore.RED}SSHPass is not installed. SSHPass is required for using SSH in this app{Style.RESET_ALL}')
                return False

            if shutil.which("ssh") is None:
                self.logger.error(f'{Fore.RED}SSH is not installed{Style.RESET_ALL}')
                return False

        if self.pwnbox_command == "terminate":
            if pwnbox_status is None:
                return False

        if self. pwnbox_command == "open":
            if pwnbox_status is None:
                return False

            if not IS_WINDOWS and shutil.which("open") is None:
                self.logger.error(f'{Fore.RED}The programme "open" is not installed. "Open" is required for opening the PwnBox Desktop.{Style.RESET_ALL}')
                return False

        return True


    def status(self):
        """Pwnbox status command"""
        pwnbox_status: PwnboxStatus = self._get_pwnbox_status()
        if pwnbox_status is None:
            return None

        self.console.print(create_pwnbox_panel(pwnbox_status.to_dict()))


    def connect_via_ssh(self):
        """Connect via SSH"""
        pwnbox_status: PwnboxStatus = self._get_pwnbox_status()
        if not self.check(pwnbox_status=pwnbox_status):
            return None

        self.logger.info(f'{Fore.GREEN}Spawning SSH connection to pwnbox{Style.RESET_ALL}')
        subprocess.run([shutil.which("sshpass"), "-p", pwnbox_status.vnc_password,
                        shutil.which("ssh"), f"{pwnbox_status.username}@{pwnbox_status.hostname}",
                        "-o", "StrictHostKeyChecking=no",
                        "-o", "UserKnownHostsFile=/dev/null"],
                        stdout=sys.stdout,
                        stderr=sys.stderr,
                        stdin=sys.stdin,
                        env=os.environ.copy())

        self.logger.info(f'{Fore.GREEN}SSH connection terminated{Style.RESET_ALL}')

    def open_vnc(self):
        """Open a connection to pwnbox"""
        pwnbox_status: PwnboxStatus = self._get_pwnbox_status()
        if not self.check(pwnbox_status):
            return None
        self.logger.info(f'{Fore.GREEN}Open PwnBox desktop in default browser{Style.RESET_ALL}')

        # We use the spectator url for getting a full vnc connection. This is done by removing the "view_only" parameter and replace the password
        url: str = f'{pwnbox_status.spectate_url.split("password=")[0]}password={pwnbox_status.vnc_password}'
        if IS_WINDOWS:
            subprocess.Popen(['powershell','-c',
                              'start',
                              url.replace('&', '`&')], # Windows does not like ampersand. This must be escaped using backticks
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
        else:
            subprocess.Popen([shutil.which("open"), url],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)


    def terminate(self):
        """Terminate pwnbox"""
        pwnbox_status: PwnboxStatus = self._get_pwnbox_status()
        if not self.check(pwnbox_status):
            return None
        status, msg = pwnbox_status.terminate()
        if status:
            self.logger.info(f'{Fore.GREEN}Pwnbox with ID "{pwnbox_status.id}" and hostname "{pwnbox_status.hostname}" terminated{Style.RESET_ALL}')
        else:
            self.logger.error(f'{Fore.RED}{msg}{Style.RESET_ALL}')


    def execute(self):
        """Execute the command"""
        if self.pwnbox_command is None:
            return None
        if self.pwnbox_command == "status":
            self.status()
        elif self.pwnbox_command == "ssh":
            self.connect_via_ssh()
        elif self.pwnbox_command == "open":
            self.open_vnc()
        elif self.pwnbox_command == "terminate":
            self.terminate()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.pwnbox_command}{Style.RESET_ALL}')


    def _get_pwnbox_status(self) -> Optional[PwnboxStatus]:
        try:
            return self.client.get_pwnbox_status()
        except NoPwnBoxActiveException as e:
            self.logger.error(f'{Fore.RED}{e}{Style.RESET_ALL}')
            return None