import argparse
from typing import Optional, List

from colorama import Fore, Style
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from command.base import BaseCommand
from console import create_prolab_info_panel_text, create_prolab_detail_info_panel
from htbapi import ProLabInfo


class ProlabsCommand(BaseCommand):
    prolabs_command: Optional[str]
    flag: Optional[str]
    changelog_limit: int

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli, args)
        self.prolabs_command: Optional[str] = args.prolabs if hasattr(args, "prolabs") else None
        self.flag = args.flag if hasattr(args, "flag") else None
        self.changelog_limit = args.limit if hasattr(args, "limit") else 20

    def checks(self):
        """Do some basic checks"""
        if self.prolabs_command in ["info", "submit", "flags", "machines", "progress", "changelog", "reset-status"]:
            if self.args.id is None and self.args.name is None:
                self.logger.error(
                    f"{Fore.RED}ID or Name must be specified. Use --help for more information.{Style.RESET_ALL}")
                return False

        if self.prolabs_command == "submit" and self.flag is None:
            self.logger.error(f"{Fore.RED}A flag must be specified.{Style.RESET_ALL}")
            return False

        return True

    def _load_prolab(self) -> Optional[ProLabInfo]:
        if not self.checks():
            return None

        prolab_info: Optional[ProLabInfo] = self.client.get_prolab(prolab_id=self.args.id, prolab_name=self.args.name)
        if not self.check_id_name(prolab_info):
            return None

        return prolab_info

    def check_id_name(self, prolab_info: Optional[ProLabInfo]):
        """Check the  id and name field"""
        if prolab_info is None:
            if self.args.id is not None:
                self.logger.error(f'{Fore.RED}No prolab found with ID "{self.args.id}"{Style.RESET_ALL}')
            else:
                self.logger.error(f'{Fore.RED}No prolab found with name "{self.args.name}"{Style.RESET_ALL}')
            return False

        return True

    def list(self):
        """Display the prolabs"""
        prolabs: List[ProLabInfo] = self.client.get_prolabs()

        table = Table.grid(expand=True)
        num_cols = 2
        for i in range(0, num_cols):
            table.add_column()


        my_dict: dict = {}
        for prolab in prolabs:
            my_dict[prolab.name] = {prolab.name: create_prolab_info_panel_text(prolab=prolab.to_dict())}

            if len(my_dict.keys()) == num_cols:
                # Adjust height so that the frames have the same height.

                adjusted_panels = []
                max_height: int = max([len(v[k].split("\n")) for k,v in my_dict.items()])
                for k, v in my_dict.items():
                    if max_height > 0:
                        lines = v[k].split("\n")
                        padding_lines = max_height - len(lines)
                        if padding_lines > 0:
                            lines.extend([""] * padding_lines)
                        v[k] = "\n".join(lines)

                    adjusted_panels.append(Panel(renderable=Text.from_markup(text=v[k], justify="left"),
                                                 title=f"[bold yellow]{k}[/bold yellow]",
                                                 expand=True,
                                                 border_style="yellow",
                                                 title_align="left"))

                # Group 3 panels in ony line
                table.add_row(*adjusted_panels)
                my_dict = {}

        # The rest of the panels (less than 3)
        if len(my_dict.keys()) > 0:
            adjusted_panels = []
            for k, v in my_dict.items():
                adjusted_panels.append(Panel(renderable=Text.from_markup(text=v[k], justify="left"),
                                             title=f"[bold yellow]{k}[/bold yellow]",
                                             expand=True,
                                             border_style="yellow",
                                             title_align="left"))
            table.add_row(*adjusted_panels)
        self.console.print(table)

    def print_info(self):
        """Print the prolabs information for one prolab"""
        prolab_info = self._load_prolab()
        if prolab_info is not None:
            self.console.print(create_prolab_detail_info_panel(prolab_dict=prolab_info.to_dict()))

    def submit(self) -> None:
        """Submit the prolab flag"""
        prolab_info = self._load_prolab()
        if prolab_info is None:
            return None

        res, msg = prolab_info.submit_flag(self.flag)
        if res:
            self.logger.info(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
        else:
            self.logger.error(f"{Fore.RED}{msg}{Style.RESET_ALL}")

        return None

    def flags(self):
        """List all flags of one ProLab."""
        prolab_info = self._load_prolab()
        if prolab_info is None:
            return None

        flags = prolab_info.get_flags()
        if flags is None or len(flags) == 0:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No flags found for ProLab "{prolab_info.name}"{Style.RESET_ALL}')
            return None

        table = Table(expand=True, show_lines=False, box=None)
        table.add_column("#", width=1)
        table.add_column("ID", width=1)
        table.add_column("Title", width=10)
        table.add_column("Points", width=1)
        table.add_column("Owned?", width=1)

        for i, flag in enumerate(flags):
            owned_text = "[bold green]✔[/bold green]" if flag.owned else "✘"
            table.add_row(f"{i + 1}",
                          f"{flag.id}",
                          f"{flag.title}",
                          f"{flag.points}",
                          owned_text)

        self.console.print(Panel(table,
                                 title=f"[bold yellow]ProLab Flags - {prolab_info.name}[/bold yellow]",
                                 border_style="yellow",
                                 title_align="left",
                                 expand=True))

    def machines(self):
        """List all machines of one ProLab."""
        prolab_info = self._load_prolab()
        if prolab_info is None:
            return None

        machines = prolab_info.get_machines()
        if machines is None or len(machines) == 0:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}No machines found for ProLab "{prolab_info.name}"{Style.RESET_ALL}')
            return None

        table = Table(expand=True, show_lines=False, box=None)
        table.add_column("#", width=1)
        table.add_column("ID", width=1)
        table.add_column("Name", width=12)
        table.add_column("OS", width=8)

        for i, machine in enumerate(machines):
            if machine.os.lower() == "windows":
                os_icon = "\U0001F5D4"
            elif machine.os.lower() in ["linux", "freebsd", "openbsd"]:
                os_icon = "\U0001F427"
            elif machine.os.lower() == "android":
                os_icon = "\U0001F4F1"
            else:
                os_icon = "-"

            table.add_row(f"{i + 1}",
                          f"{machine.id}",
                          machine.name,
                          f"{os_icon} {machine.os}")

        self.console.print(Panel(table,
                                 title=f"[bold yellow]ProLab Machines - {prolab_info.name}[/bold yellow]",
                                 border_style="yellow",
                                 title_align="left",
                                 expand=True))

    def progress(self):
        """Show progress and milestones of one ProLab."""
        prolab_info = self._load_prolab()
        if prolab_info is None:
            return None

        progress_data = prolab_info.get_progress()
        if progress_data is None:
            self.logger.warning(
                f'{Fore.LIGHTYELLOW_EX}No progress information available for ProLab "{prolab_info.name}"{Style.RESET_ALL}')
            return None

        reached_milestones = len([x for x in progress_data.milestones if x.is_milestone_reached])
        total_milestones = len(progress_data.milestones)
        overview = {
            "Ownership": f"{progress_data.ownership}%",
            "Ownership required for certificate": f"{progress_data.ownership_required_for_certification}%",
            "Milestones reached": f"{reached_milestones}/{total_milestones}",
        }
        max_key_length = max(len(key) for key in overview.keys())
        overview_text = "\n".join([f"[bold white]{k.ljust(max_key_length)}[/bold white] : [bold cyan]{v}[/bold cyan]"
                                    for k, v in overview.items()])
        overview_panel = Panel(renderable=Text.from_markup(text=overview_text, justify="left"),
                               title=f"[bold yellow]Progress Overview - {prolab_info.name}[/bold yellow]",
                               expand=True,
                               border_style="yellow",
                               title_align="left")

        if total_milestones == 0:
            self.console.print(overview_panel)
            return None

        milestone_table = Table(expand=True, show_lines=False, box=None)
        milestone_table.add_column("#", width=1)
        milestone_table.add_column("Target [%]", width=1)
        milestone_table.add_column("Milestone", width=8)
        milestone_table.add_column("Reached?", width=1)
        milestone_table.add_column("Rarity", width=1)
        milestone_table.add_column("Description", width=20)
        for i, milestone in enumerate(sorted(progress_data.milestones, key=lambda x: x.percent)):
            reached = "[bold green]✔[/bold green]" if milestone.is_milestone_reached else "✘"
            milestone_table.add_row(f"{i + 1}",
                                    f"{milestone.percent}",
                                    milestone.text,
                                    reached,
                                    f"{milestone.rarity}",
                                    milestone.description)

        milestone_panel = Panel(milestone_table,
                                title=f"[bold yellow]Milestones - {prolab_info.name}[/bold yellow]",
                                border_style="yellow",
                                title_align="left",
                                expand=True)

        self.console.print(Group(overview_panel, milestone_panel))

    def changelog(self):
        """Show changelog entries of one ProLab."""
        prolab_info = self._load_prolab()
        if prolab_info is None:
            return None

        changelog_entries = sorted(prolab_info.get_changelogs() or [], key=lambda x: x.created_at, reverse=True)
        if self.changelog_limit is not None and self.changelog_limit > 0:
            changelog_entries = changelog_entries[:self.changelog_limit]

        if changelog_entries is None or len(changelog_entries) == 0:
            self.logger.warning(
                f'{Fore.LIGHTYELLOW_EX}No changelog entries found for ProLab "{prolab_info.name}"{Style.RESET_ALL}')
            return None

        changelog_table = Table(expand=True, show_lines=False, box=None)
        changelog_table.add_column("#", width=1)
        changelog_table.add_column("Date", width=8)
        changelog_table.add_column("Type", width=3)
        changelog_table.add_column("User", width=7)
        changelog_table.add_column("Title", width=8)
        changelog_table.add_column("Description", width=25)

        for i, entry in enumerate(changelog_entries):
            entry_type = entry.type.upper()
            if entry.type.lower() == "add":
                entry_type = "[bold bright_green][+][/bold bright_green] ADD"
            elif entry.type.lower() == "update":
                entry_type = "[bold bright_blue][~][/bold bright_blue] UPDATE"
            elif entry.type.lower() == "remove":
                entry_type = "[bold bright_red][-][/bold bright_red] REMOVE"

            user_name = "-" if entry.user is None else entry.user.name

            changelog_table.add_row(f"{i + 1}",
                                    f"{entry.created_at.strftime('%Y-%m-%d %H:%M')} UTC",
                                    entry_type,
                                    user_name,
                                    entry.title.replace("\n", " "),
                                    entry.description.replace("\n", " "))

        self.console.print(Panel(changelog_table,
                                 title=f"[bold yellow]Changelog - {prolab_info.name}[/bold yellow]",
                                 border_style="yellow",
                                 title_align="left",
                                 expand=True))

    def reset_status(self):
        """Show reset status and last reset timestamp."""
        prolab_info = self._load_prolab()
        if prolab_info is None:
            return None

        msg, last_reverted = prolab_info.get_reset_status()
        status_value = "Online" if msg is None else msg
        status_color = "bold green" if msg is None else "bold yellow"

        reset_status = {
            "ProLab": prolab_info.name,
            "Reset status": f"[{status_color}]{status_value}[/{status_color}]",
            "Last reverted": "-" if last_reverted is None else f'{last_reverted.strftime("%Y-%m-%d %H:%M:%S")} UTC',
        }
        max_key_length = max(len(key) for key in reset_status.keys())
        status_text = "\n".join([f"[bold white]{k.ljust(max_key_length)}[/bold white] : {v}" for k, v in reset_status.items()])
        self.console.print(Panel(renderable=Text.from_markup(text=status_text, justify="left"),
                                 title=f"[bold yellow]Reset Status[/bold yellow]",
                                 expand=True,
                                 border_style="yellow",
                                 title_align="left"))

    def execute(self):
        """Execute the command"""
        if self.prolabs_command == "list":
            self.list()
        elif self.prolabs_command == "info":
            self.print_info()
        elif self.prolabs_command == "flags":
            self.flags()
        elif self.prolabs_command == "machines":
            self.machines()
        elif self.prolabs_command == "progress":
            self.progress()
        elif self.prolabs_command == "changelog":
            self.changelog()
        elif self.prolabs_command == "reset-status":
            self.reset_status()
        elif self.prolabs_command == "submit":
            self.submit()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.prolabs_command}{Style.RESET_ALL}')
