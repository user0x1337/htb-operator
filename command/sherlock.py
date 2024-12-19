import argparse
from typing import Optional, List

from colorama import Fore, Style

from command.base import BaseCommand
from console import create_sherlock_list_group_by_retired_panel
from htbapi import SherlockInfo, SherlockCategory


class SherlockCommand(BaseCommand):
    sherlock_command: Optional[str]
    sherlock_only_active: Optional[bool]
    sherlock_only_retired: Optional[bool]
    filter_category: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli, args)
        self.sherlock_command = args.sherlock if hasattr(args, "sherlock") else None
        self.sherlock_only_active = args.active if hasattr(args, "active") else None
        self.sherlock_only_retired = args.retired if hasattr(args, "retired") else None
        self.filter_category = args.filter_category if hasattr(args, "filter_category") else None

    def list(self):
        cats: List[SherlockCategory] = []
        if self.filter_category is not None and len(self.filter_category) > 0:
            filter_dict = {x.name.lower():x for x in self.client.get_sherlock_categories()}

            for filter_element in self.filter_category.split(","):
                if filter_element.lower() not in filter_dict.keys():
                    self.logger.warning(f'{Fore.LIGHTYELLOW_EX}Category {filter_element} not a valid sherlock category{Style.RESET_ALL}')
                    continue
                cats.append(filter_dict[filter_element.lower()])

        sherlocks: List[SherlockInfo] = self.client.get_sherlocks(only_active=self.sherlock_only_active,
                                                                  only_retired=self.sherlock_only_retired,
                                                                  filter_sherlock_category=cats)

        self.console.print(create_sherlock_list_group_by_retired_panel(
            sherlock_info=sorted([x.to_dict() for x in sherlocks],
                                 key=lambda x: (x["state"], x["name"].casefold()),
                                 reverse=False)))

    def execute(self):

        if self.sherlock_command == "list":
            self.list()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.sherlock_command}{Style.RESET_ALL}')