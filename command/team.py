import argparse
from typing import List, Optional

from colorama import Fore, Style

from command.base import BaseCommand
from console import create_teams_info_panel, create_team_invitations_table
from htbapi import User, Team


class TeamCommand(BaseCommand):
    teams_command: Optional[str]
    team_name: str

    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)

        self.teams_command = args.teams if hasattr(args, "teams") else None
        self.team_name = args.name if hasattr(args, "name") else None
        self.team_id = args.id if hasattr(args, "id") else None
        self.user_id = args.user_id if hasattr(args, "user_id") else None
        self.invitations_command = None
        if self.teams_command is not None and self.teams_command == "invitation" and hasattr(args, "team_invitations"):
            self.invitations_command = args.team_invitations


    def info(self):
        """Prints general information about the current team, its members, then overall performance"""
        if self.team_id is None and self.team_name is None:
            self.logger.error(f'{Fore.RED}No team id and no team name{Style.RESET_ALL}')
            return

        # if no team id is given, search for the team by name and get the id
        if self.team_id is None or self.team_id < 1:
            ids: List[int] = self.client.search_for_teams_by_name(self.team_name)
            if len(ids) == 0:
                self.logger.error(f'{Fore.RED}Could not find any teams with name {self.team_name}{Style.RESET_ALL}')
                return
            if len(ids) > 1:
                self.logger.error(f'{Fore.RED}Found {len(ids)} teams containing the name {self.team_name}.{Style.RESET_ALL}')
                return
            self.team_id = ids[0]

        team: Team = self.client.get_team_info(team_id=self.team_id)
        invitations: List[User] = team.get_invitations()

        self.console.print(create_teams_info_panel(team_info=team.to_dict(), team_invitations=[x.to_dict() for x in invitations]))

    def invitation_show(self):
        """Print invitations for the team"""
        if self.team_id is None and self.team_name is None:
            self.logger.error(f'{Fore.RED}No team id and no team name{Style.RESET_ALL}')
            return

        if self.team_id is None or self.team_id < 1:
            ids: List[int] = self.client.search_for_teams_by_name(self.team_name)
            if len(ids) == 0:
                self.logger.error(f'{Fore.RED}Could not find any teams with name {self.team_name}{Style.RESET_ALL}')
                return
            if len(ids) > 1:
                self.logger.error(f'{Fore.RED}Found {len(ids)} teams containing the name {self.team_name}.{Style.RESET_ALL}')
                return
            self.team_id = ids[0]

        team: Team = self.client.get_team_info(team_id=self.team_id)
        invitations: List[User] = team.get_invitations()

        self.console.print(create_team_invitations_table(team_invitations=[x.to_dict() for x in invitations], title=f'Invitations for {self.team_name}'))

    def invitation_accept(self):
        if self.user_id is None:
            self.logger.error(f'{Fore.RED}No user_id is given.{Style.RESET_ALL}')
            return

        if self.team_id is None and self.team_name is None:
            self.logger.error(f'{Fore.RED}No team id and no team name{Style.RESET_ALL}')
            return

        if self.team_id is None or self.team_id < 1:
            ids: List[int] = self.client.search_for_teams_by_name(self.team_name)
            if len(ids) == 0:
                self.logger.error(f'{Fore.RED}Could not find any teams with name {self.team_name}{Style.RESET_ALL}')
                return
            if len(ids) > 1:
                self.logger.error(f'{Fore.RED}Found {len(ids)} teams containing the name {self.team_name}.{Style.RESET_ALL}')
                return
            self.team_id = ids[0]

        team: Team = self.client.get_team_info(team_id=self.team_id)
        invitation = [x for x in team.get_invitations() if x.id == self.user_id] # TODO: Use "next"?
        print(invitation)


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
        elif self.teams_command == "invitation" and self.invitations_command == "show":
            self.invitation_show()
        elif self.teams_command == "invitation" and self.invitations_command == "accept":
            self.invitation_accept()
        elif self.teams_command == "edit":
            self.edit()
        elif self.teams_command == "kick":
            self.kick()
        elif self.teams_command == "promote":
            self.promote()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.teams_command}{Style.RESET_ALL}')








