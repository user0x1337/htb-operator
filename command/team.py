import argparse
from typing import List, Optional

from colorama import Fore, Style

from command.base import BaseCommand
from console import create_teams_info_panel
from htbapi import User, Team


class TeamCommand(BaseCommand):
    teams_command: Optional[str]
    team_name: str

    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)

        self.teams_command = args.teams if hasattr(args, "teams") else None
        self.team_name = args.name if hasattr(args, "name") else None
        self.team_id = args.id if hasattr(args, "id") else None


    def info(self) -> None:
        """Prints general information about the current team, its members, then overall performance"""
        if self.team_id is None and self.team_name is None:
            self.logger.error(f'{Fore.RED}No team id and no team name{Style.RESET_ALL}')
            return None

        # if no team id is given, search for the team by name and get the id
        if self.team_id is None or self.team_id < 1:
            ids: List[int] = self.client.search_for_teams_by_name(self.team_name)
            if len(ids) == 0:
                self.logger.error(f'{Fore.RED}Could not find any teams with name {self.team_name}{Style.RESET_ALL}')
                return None
            if len(ids) > 1:
                self.logger.error(f'{Fore.RED}Found {len(ids)} teams containing the name {self.team_name}.{Style.RESET_ALL}')
                return None
            self.team_id = ids[0]

        team: Team = self.client.get_team_info(team_id=self.team_id)
        self.console.print(create_teams_info_panel(team_info=team.to_dict()))

        return None

    def ranking(self):
        pass

    def invitation(self):
        pass # show, accept, decline

    def edit(self):
        pass # Edit name, country and motto

    def kick(self):
        pass  # kick member, after confirmation

    def promote(self):
        pass # promote to captain


    def execute(self) -> None:
        if self.teams_command is None:
            pass
        elif self.teams_command == "info":
            self.info()
        elif self.teams_command == "ranking":
            self.ranking()
        elif self.teams_command == "invitation":
            self.invitation()
        elif self.teams_command == "edit":
            self.edit()
        elif self.teams_command == "kick":
            self.kick()
        elif self.teams_command == "promote":
            self.promote()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.teams_command}{Style.RESET_ALL}')








