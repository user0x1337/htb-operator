import argparse

from command import ApiKey
from command.base import BaseCommand

DEFAULT_BASE_API_URL = "https://labs.hackthebox.com/api/"

class InitCommand(BaseCommand):

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        self.api_command = ApiKey(htb_cli=self.htb_cli, args=args)


    def execute(self):
        """Execute the init command"""
        htb_dict = dict()
        windows_dict = dict()
        if self.args.apikey:
            # Check API-Key
            if self.api_command.check_api_key(self.args.apikey):
                htb_dict = {'api_key': self.args.apikey}
            else:
                return None

        if self.args.apiurl:
            htb_dict['api_base_url'] = self.args.apiurl
        else:
            htb_dict['api_base_url'] = DEFAULT_BASE_API_URL

        htb_dict["USER_AGENT"] = f"{self.htb_cli.package_name}/{self.htb_cli.version}"
        htb_dict["DOWNLOAD_COOLDOWN"] = 30

        windows_dict["OpenVPN-Path"] = ""

        self.htb_cli.config["HTB"] = htb_dict
        self.htb_cli.config["WINDOWS"] = windows_dict
        self.htb_cli.save_config_file()
        self.logger.info("HTB-Operator successfully initialized.")