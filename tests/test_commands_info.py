from __future__ import annotations

import argparse

import pytest

import command.info as info_mod
from command.info import InfoCommand


class LoggerStub:
    def __init__(self) -> None:
        self.infos = []
        self.warnings = []
        self.errors = []

    def info(self, msg: str) -> None:
        self.infos.append(msg)

    def warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def error(self, msg: str) -> None:
        self.errors.append(msg)


class ConsoleStub:
    def __init__(self) -> None:
        self.printed = []

    def print(self, obj) -> None:
        self.printed.append(obj)


class UserStub:
    def __init__(self) -> None:
        self.id = 1

    def to_dict(self, key_filter=None) -> dict:
        return {"ID": 1, "Name": "tester"}


class InfoClientStub:
    def __init__(self) -> None:
        self.user = UserStub()

    def get_user(self, username=None):
        return self.user

    def get_user_activity(self, user_id: int):
        return ["activity"]

    def get_fortress_progress_profile_summary(self, user_id: int):
        raise AssertionError("fortress progress should not be called when --activity is set")

    def get_prolab_progress_profile_summary(self, user_id: int):
        raise AssertionError("prolab progress should not be called when --activity is set")

    def get_sherlock_progress_profile_summary(self, user_id: int):
        raise AssertionError("sherlock progress should not be called when --activity is set")

    def get_machine_progress_profile_summary(self, user_id: int):
        raise AssertionError("machine progress should not be called when --activity is set")

    def get_challenge_progress_profile_summary(self, user_id: int):
        raise AssertionError("challenge progress should not be called when --activity is set")


class CLIStub:
    def __init__(self) -> None:
        self.logger = LoggerStub()
        self.console = ConsoleStub()
        self.client = InfoClientStub()



def test_info_command_activity_only(monkeypatch) -> None:
    cli = CLIStub()
    args = argparse.Namespace(activity=True, username=None)

    sentinel = object()
    monkeypatch.setattr(info_mod, "create_activity_panel", lambda activity_list, limit_activity_entries=None: sentinel)

    cmd = InfoCommand(htb_cli=cli, args=args)
    cmd.execute()

    assert cli.console.printed == [sentinel]
