import argparse
from typing import Optional, List

from colorama import Fore, Style

from command.base import BaseCommand
from console import create_table_badge_list
from htbapi import BadgeCategory


class BadgeCommand(BaseCommand):
    badge_command: Optional[str]
    user_id: Optional[int]
    username: Optional[str]
    open: bool

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        self.badge_command = self.args.badge if hasattr(self.args, "badge") else None
        self.user_id = self.args.user_id if hasattr(self.args, "user_id") else None
        self.username = self.args.username if hasattr(self.args, "username") else None
        self.open = self.args.open if hasattr(self.args, "open") else False

    def list(self):
        """List all badges"""
        badges: List[BadgeCategory] = self.client.get_badges(user_id=self.user_id, username=self.username, remove_obtained_badges=self.open)
        self.console.print(create_table_badge_list(badge_categories=[x.to_dict() for x in badges]))

    def execute(self):
        """Execute the command"""
        if self.badge_command is None:
            self.logger.error(f'{Fore.RED}Badge command is missing{Style.RESET_ALL}')
            return None

        if self.badge_command == "list":
            self.list()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.badge_command}{Style.RESET_ALL}')
            return None
