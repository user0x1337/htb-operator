import argparse
from typing import Optional, List

from colorama import Fore, Style
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from command.base import BaseCommand
from console import create_prolab_info_panel_text, create_prolab_detail_info_panel
from htbapi import ProLabInfo


class ProlabsCommand(BaseCommand):
    prolabs_command: Optional[str]
    flag: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli, args)
        self.prolabs_command: Optional[str] = args.prolabs if hasattr(args, "prolabs") else None
        self.flag = args.flag if hasattr(args, "flag") else None

    def checks(self):
        """Do some basic checks"""
        if self.prolabs_command in ["info", "submit"]:
            if self.args.id is None and self.args.name is None:
                self.logger.error(
                    f"{Fore.RED}ID or Name must be specified. Use --help for more information.{Style.RESET_ALL}")
                return False

        if self.prolabs_command == "submit" and self.flag is None:
            self.logger.error(f"{Fore.RED}A flag must be specified.{Style.RESET_ALL}")
            return False

        return True

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
        if not self.checks():
            return None

        # Need to get the prolab id first
        prolab_info: Optional[ProLabInfo] = self.client.get_prolab(prolab_id=self.args.id, prolab_name=self.args.name)
        if not self.check_id_name(prolab_info):
            return None

        self.console.print(create_prolab_detail_info_panel(prolab_dict=prolab_info.to_dict()))

    def submit(self):
        """Submit the prolab flag"""
        if not self.checks():
            return None

        prolab_info: Optional[ProLabInfo] = self.client.get_prolab(prolab_id=self.args.id, prolab_name=self.args.name)
        if not self.check_id_name(prolab_info):
            return None

        res, msg = prolab_info.submit_flag(self.flag)
        if res:
            self.logger.info(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
        else:
            self.logger.error(f"{Fore.RED}{msg}{Style.RESET_ALL}")


    def execute(self):
        """Execute the command"""
        if self.prolabs_command == "list":
            self.list()
        elif self.prolabs_command == "info":
            self.print_info()
        elif self.prolabs_command == "submit":
            self.submit()
        else:
            self.logger.error(f'{Fore.RED}Unknown command: {self.prolabs_command}{Style.RESET_ALL}')
