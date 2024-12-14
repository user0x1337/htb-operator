import argparse
from typing import List, Optional

from colorama import Fore, Style
from rich.table import Table

from command.base import BaseCommand
from console.cli_panel import format_bool, create_profile_panel, create_ranking_panel, create_misc_panel, \
    create_advanced_labs_panel, create_activity_panel
from htbapi import ChallengeList, User, Activity, FortressUserProfile, ProLabUserProfile, EndgameUserProfile, \
    SherlockUserProfile, MachineOsUserProfile, ChallengeUserProfile


class InfoCommand(BaseCommand):
    challenge_name: Optional[str]
    username: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        self.challenge_name = args.c if hasattr(args, "c") else None
        self.username = args.username if hasattr(args, "username") else None


    def execute(self):
        if self.challenge_name:
            challenges_list: List[ChallengeList] = self.client.search_challenges(name=self.challenge_name)
            if len(challenges_list) == 0:
                self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No challenges found for name "{self.challenge_name}"{Style.RESET_ALL}')
                return None

            categories = self.client.get_challenge_categories_list()
            category_dict = {x.id: x.name for x in categories}

            table = Table(title="Challenges", show_lines=True)
            table.add_column(header="ID", style="cyan", justify="left")
            table.add_column(header="Name", style="cyan", justify="left")
            table.add_column(header="Retired", style="cyan", justify="left")
            table.add_column(header="Difficulty", style="cyan", justify="left")
            table.add_column(header="Solved", style="cyan", justify="left")
            table.add_column(header="Release Date", style="cyan", justify="left")
            table.add_column(header="Category", style="cyan", justify="left")

            for c in challenges_list:
                table.add_row(str(c.id),
                              c.name,
                              format_bool(c.retired),
                              c.difficulty,
                              format_bool(c.solved),
                              f"{c.release_date.strftime('%Y-%m-%d')}",
                              category_dict[c.category_id])

            self.console.print(table)
        else:
            user: User = self.client.get_user(self.username)
            activities: List[Activity] = self.client.get_user_activity(user_id=user.id)
            if not self.args.activity:
                fortress_progress: List[FortressUserProfile] = self.client.get_fortress_progress_profile_summary(user_id=user.id)
                prolabs_progress: List[ProLabUserProfile] = self.client.get_prolab_progress_profile_summary(user_id=user.id)
                endgame_progress: List[EndgameUserProfile] = self.client.get_endgame_progress_profile_summary(user_id=user.id)
                sherlocks_progress: List[SherlockUserProfile] = self.client.get_sherlock_progress_profile_summary(user_id=user.id)
                machines_os_progress: List[MachineOsUserProfile] = self.client.get_machine_progress_profile_summary(user_id=user.id)
                challenge_progress: List[ChallengeUserProfile] = self.client.get_challenge_progress_profile_summary(user_id=user.id)

                panel_profile = create_profile_panel(user_dict=user.to_dict(key_filter=["ID", "Name", "Team", "University", "Country", "Subscription"]))
                panel_ranking = create_ranking_panel(ranking_dict=user.to_dict(key_filter=["Ranking", "Ranking_Bracket", "Team", "University", "Points", "Rank", "Ownership", "Next Rank", "Rank Requirement"]))
                panel_misc = create_misc_panel(misc_dict=user.to_dict(key_filter=["User Bloods", "System Bloods", "User Owns", "System Owns", "Respects", "Public"]))

                max_panel_height = max(len(fortress_progress), len(sherlocks_progress), len(endgame_progress))
                panel_fortress = create_advanced_labs_panel(advanced_list=fortress_progress, title="🏰 Fortress Progress", target_height=max_panel_height)
                panel_sherlocks = create_advanced_labs_panel(advanced_list=sherlocks_progress, title="🛡️  Sherlock Progress", target_height=max_panel_height)
                panel_endgames = create_advanced_labs_panel(advanced_list=endgame_progress, title="🎯 Endgame Progress", target_height=max_panel_height)

                max_panel_height_2 = max(len(prolabs_progress), len(machines_os_progress), len(challenge_progress))
                panel_prolabs = create_advanced_labs_panel(advanced_list=prolabs_progress, title="🏆 Prolab Progress", target_height=max_panel_height_2)
                panel_machines = create_advanced_labs_panel(advanced_list=machines_os_progress, title="💻 Machine Progress", target_height=max_panel_height_2)
                panel_challenges = create_advanced_labs_panel(advanced_list=challenge_progress, title="⚔️  Challenge Progress", target_height=max_panel_height_2)


                table = Table.grid(expand=True)
                table.add_column()
                table.add_column()
                table.add_row(panel_profile, panel_ranking, panel_misc)
                table.add_row(panel_fortress, panel_sherlocks, panel_endgames)
                table.add_row(panel_prolabs, panel_challenges, panel_machines)

                self.console.print(table)

            panel_activity = create_activity_panel(activity_list=activities, limit_activity_entries=20 if not self.args.activity else None)
            self.console.print(panel_activity)