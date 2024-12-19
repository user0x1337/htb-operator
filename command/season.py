import argparse
from typing import Optional, List

from colorama import Fore, Style
from rich.panel import Panel
from rich.table import Table

from command.base import BaseCommand
from console import create_season_list_table, create_season_panel
from htbapi import SeasonList, User, SeasonUserDetails


class SeasonCommand(BaseCommand):
    seasons_command: Optional[str]
    season_ids: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli, args)
        self.seasons_command = args.seasons if hasattr(args, "seasons") else None
        self.username = args.username if hasattr(args, "username") else None
        self.season_ids = args.ids if hasattr(args, "ids") else None

    def checks(self, obj) -> bool:
        if self.seasons_command == "info":
            if obj is None:
                self.logger.error(f'{Fore.RED}No user found for username "{self.username}"{Style.RESET_ALL}')
                return False
            if self.season_ids is not None:
                try:
                    [int(x.strip()) for x in self.season_ids.split(",")]
                except ValueError:
                    self.logger.error(f'{Fore.RED}Only numbers are allowed{Style.RESET_ALL}')
                    return False

        return True

    def list(self):
        """Lists the seasons"""
        seasons: List[SeasonList] = self.client.get_season_list()
        if seasons is None or len(seasons) == 0:
            self.logger.warning(f"{Fore.LIGHTYELLOW_EX}No seasons found{Style.RESET_ALL}")
            return None

        seasons = sorted(seasons, key=lambda s: s.start_date, reverse=True)
        self.console.print(create_season_list_table(seasons=[x.to_dict() for x in seasons]))

    def info(self):
        """Get details about the seasons"""
        user: User = self.client.get_user(self.username)
        if not self.checks(obj=user):
            return None

        season_list: List[SeasonList] = self.client.get_season_list()
        if self.season_ids is not None:
            season_list = [x for x in season_list if x.id in [int(sid) for sid in self.season_ids.split(",")]]
            if len(season_list) == 0:
                self.logger.warning(f'{Fore.LIGHTYELLOW_EX}There are no season for id(s) "{self.season_ids}"{Style.RESET_ALL}')
                return None

        season_details: dict[int, SeasonUserDetails] = {}
        for season in season_list:
            season_details[season.id] = self.client.get_season_details(user_id=user.id, season_id=season.id)
        season_details_ids = sorted(season_details.keys(), key=lambda s: s, reverse=False)

        table = Table.grid(expand=len(season_details_ids) >= 4)
        table.add_column()
        table.add_column()

        panels = []
        for season_id in season_details_ids:
            season_meta = next(x for x in season_list if x.id == season_id)
            if season_details[season_id] is None:
                season_dict = {
                    "season_id": season_id,
                    "name": season_meta.name,
                    "tier": "-",
                    "user_name": user.name,
                    "current_rank": "-",
                    "total_ranks": "-",  # TODO: Get it from the v4/season/players/leaderboard?season=SEASON_ID API
                    "user_flags_pawned": "-",
                    "user_bloods_pawned": "-",
                    "root_flags_pawned": "-",
                    "root_bloods_pawned": "-",
                    "total_machines": "-"
                }
            else:
                season_dict = season_details[season_id].to_dict()

            season_dict["start_date"] = season_meta.start_date.strftime("%Y-%m-%d %H:%M")
            season_dict["end_date"] = season_meta.end_date.strftime("%Y-%m-%d %H:%M") if season_meta.end_date else "-"
            panels.append(create_season_panel(season_dict=season_dict))
            if len(panels) == 4:
                table.add_row(*panels)
                panels = []

        table.add_row(*panels)
        self.console.print(table)


    def execute(self):
        """Execute the command"""
        if self.seasons_command is None:
            return None
        if self.seasons_command == "list":
            self.list()
        elif self.seasons_command == "info":
            self.info()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.seasons_command}{Style.RESET_ALL}')