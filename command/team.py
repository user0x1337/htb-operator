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
        if self.team_id is None:
            self.logger.error(f'{Fore.RED}No team id{Style.RESET_ALL}')
            return None

        user: List[User] = self.client.get_team_members(team_id=self.team_id)
        self.logger.info(f"{user[0].team}, members: {user}")

        return None

    def execute(self) -> None:
        if self.teams_command is None:
            pass
        elif self.teams_command == "info":
            self.info()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.teams_command}{Style.RESET_ALL}')
