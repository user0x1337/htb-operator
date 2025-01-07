import argparse
from typing import List

from academy_api import BadgeCategory
from command.base import BaseCommand
from console import create_table_badge_list


class BadgeCommand(BaseCommand):

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        self.badge_command = self.args.badge if hasattr(self.args, "badge") else None

    def list(self):
        badges: List[BadgeCategory] = self.academy_client.get_badges()
        self.console.print(create_table_badge_list(badge_categories=[x.to_dict() for x in badges], academy=True))

    def execute(self) -> None:
        if self.badge_command == "list":
            self.list()
        else:
            raise NotImplementedError