import argparse

from command.base import BaseCommand


class InitCommand(BaseCommand):

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)


    def execute(self):
        raise NotImplementedError("Not implemented yet")