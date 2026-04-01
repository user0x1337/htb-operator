import argparse
from typing import Optional, List

from colorama import Fore, Style

from command.base import BaseCommand
from console import create_sherlock_list_group_by_retired_panel


class FortressCommand(BaseCommand):
    fortress_command: Optional[str]
    filter_category: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli, args)
        self.fortress_command = args.fortress if hasattr(args, "fortress") else None

    def list(self):
        fortress = self.client.get_fortress_list()
        #TODO: do it
        #FIXME here..

    def execute(self):
        if self.fortress_command == "list":
            self.list()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.fortress_command}{Style.RESET_ALL}')