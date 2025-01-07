import argparse

import requests
from colorama import Fore, Style
from urllib3.exceptions import InsecureRequestWarning

from command.base import BaseCommand


class InitCommand(BaseCommand):
    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


    def execute(self) -> None:
        config = self.htb_cli.config
        res, data = self.academy_client.login()
        if not res:
            self.logger.error(f"{Fore.RED}{data}{Style.RESET_ALL}")
            return None

        self.logger.info(f"{Fore.GREEN}Login successful{Style.RESET_ALL}")
        self.logger.info(f"{Fore.GREEN}Session tokens saved. Init completed. Having fun with academy commands.{Style.RESET_ALL}")

        htb_academy_dict = {"cookies": data}
        config["HTB_ACADEMY"] = htb_academy_dict
        self.htb_cli.config = config
        self.htb_cli.save_config_file()
