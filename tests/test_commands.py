from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from command.api_key import ApiKey
from command.config import ConfigCommand
from command.init import InitCommand, DEFAULT_BASE_API_URL
from command.proxy import ProxyCommand
from command.respect import RespectCommand
from command.version import VersionCommand


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


class ClientStub:
    def __init__(self) -> None:
        self.get_user_calls = []
        self.respect_calls = []

    def get_user(self, username=None, user_id=None):
        self.get_user_calls.append((username, user_id))
        return type("User", (), {"id": 1337})()

    def give_user_respect(self, user_id: int) -> None:
        self.respect_calls.append(user_id)


class CLIStub:
    def __init__(self) -> None:
        self.logger = LoggerStub()
        self.console = ConsoleStub()
        self.config = {"HTB": {}}
        self.package_name = "htb-operator"
        self.version = "1.0.0"
        self.proxy = None
        self.api_key = None
        self.client = ClientStub()
        self.save_count = 0

    def save_config_file(self) -> None:
        self.save_count += 1


class ResponseStub:
    def __init__(self, version: str, error: Exception | None = None) -> None:
        self._version = version
        self._error = error

    def raise_for_status(self) -> None:
        if self._error:
            raise self._error

    def json(self) -> dict:
        return {"info": {"version": self._version}}


def make_token(expiration: datetime) -> str:
    return jwt.encode({"exp": int(expiration.timestamp())}, key="secret", algorithm="HS256")


def test_api_key_check_valid_and_expired() -> None:
    cli = CLIStub()
    args = argparse.Namespace(check=True, renew=None)
    cmd = ApiKey(htb_cli=cli, args=args)

    valid_token = make_token(datetime.now(timezone.utc) + timedelta(hours=1))
    expired_token = make_token(datetime.now(timezone.utc) - timedelta(hours=1))

    assert cmd.check_api_key(valid_token) is True
    assert cmd.check_api_key(expired_token) is False
    assert any("API Key is valid" in msg for msg in cli.logger.infos)
    assert any("expired" in msg for msg in cli.logger.errors)


def test_api_key_check_invalid_token() -> None:
    cli = CLIStub()
    args = argparse.Namespace(check=True, renew=None)
    cmd = ApiKey(htb_cli=cli, args=args)

    assert cmd.check_api_key("not-a-jwt") is False
    assert any("Invalid JWT token" in msg for msg in cli.logger.errors)


def test_api_key_execute_renew_updates_config(monkeypatch) -> None:
    cli = CLIStub()
    cli.config = {"HTB": {"api_key": "old"}}
    args = argparse.Namespace(check=False, renew="new-token")
    cmd = ApiKey(htb_cli=cli, args=args)

    monkeypatch.setattr(ApiKey, "check_api_key", lambda *_: True)
    cmd.execute()

    assert cli.config["HTB"]["api_key"] == "new-token"
    assert cli.save_count == 1


def test_config_command_toggles_verify_ssl() -> None:
    cli = CLIStub()
    args = argparse.Namespace(no_verify_ssl=True, verify_ssl=False)
    ConfigCommand(htb_cli=cli, args=args).execute()

    assert cli.config["HTB"]["verify_ssl"] == "False"
    assert cli.save_count == 1


def test_proxy_command_clear_and_set() -> None:
    cli = CLIStub()
    cli.config["Proxy"] = {"http": "http://old"}

    clear_args = argparse.Namespace(clear=True, http=None)
    ProxyCommand(htb_cli=cli, args=clear_args).execute()
    assert "Proxy" not in cli.config

    set_args = argparse.Namespace(clear=False, http="http://a,https://b")
    ProxyCommand(htb_cli=cli, args=set_args).execute()
    assert cli.config["Proxy"]["http"] == "http://a"
    assert cli.config["Proxy"]["https"] == "https://b"
    assert cli.save_count == 2


def test_init_command_defaults_and_user_agent(monkeypatch) -> None:
    cli = CLIStub()
    args = argparse.Namespace(apikey=None, apiurl=None)
    cmd = InitCommand(htb_cli=cli, args=args)

    cmd.execute()

    assert cli.config["HTB"]["api_base_url"] == DEFAULT_BASE_API_URL
    assert cli.config["HTB"]["USER_AGENT"] == f"{cli.package_name}/{cli.version}"
    assert cli.save_count == 1


def test_init_command_with_apikey(monkeypatch) -> None:
    cli = CLIStub()
    args = argparse.Namespace(apikey="token", apiurl="https://custom")
    cmd = InitCommand(htb_cli=cli, args=args)

    monkeypatch.setattr(cmd.api_command, "check_api_key", lambda *_: True)
    cmd.execute()

    assert cli.config["HTB"]["api_key"] == "token"
    assert cli.config["HTB"]["api_base_url"] == "https://custom"


def test_respect_command_calls_client() -> None:
    cli = CLIStub()
    args = argparse.Namespace()
    RespectCommand(htb_cli=cli, args=args).execute()

    assert cli.client.get_user_calls == [("m4cz", None)]
    assert cli.client.respect_calls == [1337]


def test_version_command_execute_prints_version() -> None:
    cli = CLIStub()
    args = argparse.Namespace(check=False)
    cmd = VersionCommand(htb_cli=cli, args=args)

    cmd.execute()

    assert any("version" in msg for msg in cli.logger.infos)


def test_version_command_check_latest(monkeypatch) -> None:
    cli = CLIStub()
    args = argparse.Namespace(check=True)
    cmd = VersionCommand(htb_cli=cli, args=args)

    monkeypatch.setattr("command.version.requests.get", lambda **_: ResponseStub("1.0.0"))

    cmd.check_for_update()

    assert any("latest version" in msg for msg in cli.logger.infos)


def test_version_command_check_outdated_user_declines(monkeypatch) -> None:
    cli = CLIStub()
    args = argparse.Namespace(check=True)
    cmd = VersionCommand(htb_cli=cli, args=args)

    monkeypatch.setattr("command.version.requests.get", lambda **_: ResponseStub("2.0.0"))
    monkeypatch.setattr("builtins.input", lambda *_: "n")

    cmd.check_for_update()

    assert any("new version" in msg for msg in cli.logger.warnings)


def test_version_command_check_outdated_user_accepts(monkeypatch) -> None:
    cli = CLIStub()
    args = argparse.Namespace(check=True)
    cmd = VersionCommand(htb_cli=cli, args=args)

    called = {"count": 0}
    monkeypatch.setattr("command.version.requests.get", lambda **_: ResponseStub("2.0.0"))
    monkeypatch.setattr("builtins.input", lambda *_: "y")
    monkeypatch.setattr(cmd, "update", lambda *_: called.__setitem__("count", called["count"] + 1))

    cmd.check_for_update()

    assert called["count"] == 1
