import argparse

import requests
from colorama import Fore, Style

from command.base import BaseCommand



class VersionCommand(BaseCommand):

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        self.url = f"https://pypi.org/pypi/{self.htb_cli.package_name}/json"

    def check_for_update(self):
        """Check for update"""
        try:
            response = requests.get(url=self.url, timeout=10, proxies=self.proxy)
            response.raise_for_status()
            latest_version = response.json()["info"]["version"]
        except requests.RequestException as e:
            self.logger.error(f"{Fore.RED}Error while fetching version information: {e}{Style.RESET_ALL}")
            return
        if self.htb_cli.version == latest_version:
            self.logger.info(f"{Fore.GREEN}You are using the latest version ({self.htb_cli.version}){Style.RESET_ALL}")
        else:
            self.logger.warning(
                f"{Fore.LIGHTYELLOW_EX}A new version of '{self.htb_cli.package_name}' is available: {latest_version}.\n"
                f"You have version {self.htb_cli.version} installed.{Style.RESET_ALL}")

    def execute(self):
        self.logger.info(f"{Fore.CYAN}HTB-Operator version {self.htb_cli.version}{Style.RESET_ALL}")