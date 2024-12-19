import argparse
import shutil
import subprocess
import sys

import requests
from colorama import Fore, Style
from packaging.version import Version, InvalidVersion

from command.base import BaseCommand

class VersionCommand(BaseCommand):
    check: bool

    # noinspection PyUnresolvedReferences
    def __init__(self,
                 htb_cli: "HtbCLI",
                 args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)

        self.url = f"https://pypi.org/pypi/{self.htb_cli.package_name}/json"
        self.check = self.args.check if hasattr(args, "check") else False

    def update(self, latest_version):
        """Update the programme"""
        # pipx is preferred. If it is not found, use pip as the standard tool
        try:
            pipx_path = shutil.which("pipx")
            if pipx_path is not None:
                subprocess.call([pipx_path, "uninstall", f'{self.htb_cli.package_name}'], stdout=sys.stdout,stderr=sys.stderr, start_new_session=True)
                subprocess.call([pipx_path, "install", f'{self.htb_cli.package_name}'], stdout=sys.stdout, stderr=sys.stderr, start_new_session=True)
            else:
                subprocess.call([shutil.which("pip"), "install", "--upgrade", self.htb_cli.package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.logger.info(f'{Fore.GREEN}{self.htb_cli.package_name} successfully updated.{Style.RESET_ALL}')
        except subprocess.CalledProcessError as e:
            self.logger.error(f'{Fore.RED}Error during update: {e}{Style.RESET_ALL}')


    def check_for_update(self):
        """Check for update"""
        try:
            response = requests.get(url=self.url, timeout=10, proxies=self.htb_cli.proxy)
            response.raise_for_status()
            latest_version = response.json()["info"]["version"]
        except requests.RequestException as e:
            self.logger.error(f"{Fore.RED}Error while fetching version information: {e}{Style.RESET_ALL}")
            return
        try:
            if Version(self.htb_cli.version) >= Version(latest_version):
                self.logger.info(f"{Fore.GREEN}You are using the latest version ({self.htb_cli.version}){Style.RESET_ALL}")
            else:
                self.logger.warning(f"{Fore.LIGHTYELLOW_EX}A new version of '{self.htb_cli.package_name}' is available: {latest_version}{Style.RESET_ALL}")
                self.logger.warning(f"{Fore.LIGHTYELLOW_EX}You have version {self.htb_cli.version} installed.{Style.RESET_ALL}")

                try:
                    resp = input(f"\n{Fore.LIGHTYELLOW_EX}Do you wish to update? (y/N): {Style.RESET_ALL}")
                except KeyboardInterrupt:
                    return None

                if resp is None or len(resp) == 0 or resp.lower() != "y":
                    return None

                self.update(latest_version)
        except InvalidVersion as e:
            self.logger.error(f'{Fore.RED}Invalid version: {e}{Style.RESET_ALL}')

    def execute(self):
        """Execute command"""
        if self.check:
            self.check_for_update()
        else:
            self.logger.info(f"{Fore.GREEN}HTB-Operator version {self.htb_cli.version}{Style.RESET_ALL}")