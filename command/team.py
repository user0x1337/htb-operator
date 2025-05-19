import argparse
from typing import List, Optional

from colorama import Fore, Style

from command.base import BaseCommand
from htbapi import User


class TeamCommand(BaseCommand):
    teams_command: Optional[str]
    team_name: str

    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)

        self.teams_command = args.teams if hasattr(args, "teams") else None
        self.team_name = args.name if hasattr(args, "name") else None
        self.team_id = args.id if hasattr(args, "id") else None


    def info(self) -> None:
        """Prints general information about the current team, its members then overall performance"""
        if self.team_id is None:
            self.logger.error(f'{Fore.RED}No team id{Style.RESET_ALL}')
            return None

        # TODO: Accept team name and looks for the corresponding ID using API "search/fetch?query=NAME&tags=%5B%22teams%22%5D"
        # TODO: -> Or move the search algorithm into get_team_info ...

        user: List[User] = self.client.get_team_members(team_id=self.team_id)
        self.logger.info(f"{user[0].team}, members: {user}")

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








