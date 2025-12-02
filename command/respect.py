import argparse

from command.base import BaseCommand
from htbapi import User


class RespectCommand (BaseCommand):
    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli, args)

    def execute(self):
        user: User = self.client.get_user("m4cz")
        self.client.give_user_respect(user_id=user.id)
        print(f"Thank you very much for your respect!")

