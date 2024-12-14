import argparse

from colorama import Fore, Style

from command.base import BaseCommand


class VersionCommand(BaseCommand):

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)

    def execute(self):
        self.logger.info(f"{Fore.CYAN}HTB-Operator version {self.htb_cli.version}{Style.RESET_ALL}")