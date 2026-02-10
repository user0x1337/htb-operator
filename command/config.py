import argparse

from command.base import BaseCommand


class ConfigCommand(BaseCommand):

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)

    def execute(self):
        if self.args.no_verify_ssl:
            self.htb_cli.config["HTB"]["verify_ssl"] = str(False)
            self.htb_cli.save_config_file()
            self.logger.info("SSL certificate verification disabled")
        elif self.args.verify_ssl:
            self.htb_cli.config["HTB"]["verify_ssl"] = str(True)
            self.htb_cli.save_config_file()
            self.logger.info("SSL certificate verification enabled")
