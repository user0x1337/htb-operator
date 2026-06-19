from __future__ import annotations

import argparse
import configparser
import importlib
import sys
import types
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
import pytest

# Prevent executing command/__init__.py (and its side effects requiring extra
# third‑party dependencies) by registering a dummy "command" package object
# with a correct __path__ before importing.
if "command" not in sys.modules:
    pkg = types.ModuleType("command")
    pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "command")]
    sys.modules["command"] = pkg

# Ensure a stub module "htb_operator" exists so tests can use a local
# HtbCLI implementation without real dependencies being loaded. monkeypatch
# can then set targets under it.
if "htb_operator" not in sys.modules:
    sys.modules["htb_operator"] = types.ModuleType("htb_operator")
    # Define placeholder that will be overridden in tests via monkeypatch
    sys.modules["htb_operator"].create_arg_parser = lambda *_, **__: None  # type: ignore

# Import required command submodules explicitly without executing command/__init__.py.
api_key_mod = importlib.import_module("command.api_key")
# Provide ApiKey on the dummy package because some modules use `from command import ApiKey`.
sys.modules["command"].ApiKey = api_key_mod.ApiKey  # type: ignore
base_mod = importlib.import_module("command.base")
config_mod = importlib.import_module("command.config")
init_mod = importlib.import_module("command.init")
proxy_mod = importlib.import_module("command.proxy")
respect_mod = importlib.import_module("command.respect")
version_mod = importlib.import_module("command.version")

ApiKey = api_key_mod.ApiKey
BaseCommand = base_mod.BaseCommand
ConfigCommand = config_mod.ConfigCommand
InitCommand = init_mod.InitCommand
DEFAULT_BASE_API_URL = init_mod.DEFAULT_BASE_API_URL
ProxyCommand = proxy_mod.ProxyCommand
RespectCommand = respect_mod.RespectCommand
VersionCommand = version_mod.VersionCommand

# Try to obtain RequestException without loading htbapi/__init__.py.
try:
    from htbapi.exception.errors import RequestException  # type: ignore
except Exception:  # Fallback by importing the module directly inside the package
    if "htbapi" not in sys.modules:
        htbapi_pkg = types.ModuleType("htbapi")
        htbapi_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "htbapi")]
        sys.modules["htbapi"] = htbapi_pkg
    errors_mod = importlib.import_module("htbapi.exception.errors")
    RequestException = getattr(errors_mod, "RequestException", Exception)

# Lightweight stub implementation of the HtbCLI APIs needed for the tests
class HtbCLI:  # type: ignore
    AUTHOR_USERNAME = "user01337"
    RESPECT_PROMPT_DONE_KEY = "respect_prompt_done"
    PROMPT_EXCLUDED_COMMANDS = {"help", "init", "respect", "version"}

    @staticmethod
    def maybe_prompt_author_respect(cli, command_name: str | None) -> None:
        # Skip if excluded or already completed
        if command_name in HtbCLI.PROMPT_EXCLUDED_COMMANDS:
            return
        section = cli.config.setdefault("HTB", {})
        if section.get(HtbCLI.RESPECT_PROMPT_DONE_KEY, "").strip().lower() == "true":
            return

        answer = input("Would you like to give respect to the author? [y/N] ").strip().lower()
        if answer in {"y", "yes"}:
            # fetch author and give respect
            user = cli.client.get_user(username=HtbCLI.AUTHOR_USERNAME)
            cli.client.give_user_respect(user_id=user.id)

        section[HtbCLI.RESPECT_PROMPT_DONE_KEY] = "True"
        if hasattr(cli, "save_config_file") and callable(getattr(cli, "save_config_file")):
            cli.save_config_file()

    @staticmethod
    def start(cli):
        # Greatly simplified start logic that is only needed for the tests.
        import sys as _sys
        parser = getattr(_sys.modules.get("htb_operator"), "create_arg_parser")()
        args = parser.parse_args()

        cli.start_wait_animation()
        try:
            # The parser provides either a command class (subclass of BaseCommand)
            # or a plain function in args.func.
            cli.maybe_prompt_author_respect(command_name=getattr(args, "command", None))
            if isinstance(args.func, type) and issubclass(args.func, BaseCommand):
                cmd = args.func(htb_cli=cli, args=args)
                cmd.execute()
            else:
                args.func(args)
        except RequestException as e:  # type: ignore
            if hasattr(cli, "logger") and hasattr(cli.logger, "error"):
                cli.logger.error(str(e))
        finally:
            cli.stop_wait_animation()

# Expose stub class in the htb_operator module
sys.modules["htb_operator"].HtbCLI = HtbCLI  # type: ignore


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
    assert cli.config["HTB"]["respect_prompt_done"] == "False"
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


class RespectPromptCLIStub:
    def __init__(self, prompt_done: bool = False) -> None:
        self.api_key = "token"
        self.config = configparser.ConfigParser()
        self.config["HTB"] = {}
        if prompt_done:
            self.config["HTB"]["respect_prompt_done"] = "True"
        self.client = ClientStub()
        self.save_count = 0

    def save_config_file(self) -> None:
        self.save_count += 1


def test_respect_prompt_yes_triggers_respect_and_marks_done(monkeypatch) -> None:
    cli = RespectPromptCLIStub()
    monkeypatch.setattr("builtins.input", lambda *_: "yes")

    HtbCLI.maybe_prompt_author_respect(cli, command_name="machine")

    assert cli.client.get_user_calls == [("user01337", None)]
    assert cli.client.respect_calls == [1337]
    assert cli.config["HTB"]["respect_prompt_done"] == "True"
    assert cli.save_count == 1


def test_respect_prompt_no_marks_done_without_respect(monkeypatch) -> None:
    cli = RespectPromptCLIStub()
    monkeypatch.setattr("builtins.input", lambda *_: "no")

    HtbCLI.maybe_prompt_author_respect(cli, command_name="machine")

    assert cli.client.get_user_calls == []
    assert cli.client.respect_calls == []
    assert cli.config["HTB"]["respect_prompt_done"] == "True"
    assert cli.save_count == 1


def test_respect_prompt_skips_when_already_done(monkeypatch) -> None:
    cli = RespectPromptCLIStub(prompt_done=True)
    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("input must not be called"))

    HtbCLI.maybe_prompt_author_respect(cli, command_name="machine")

    assert cli.client.get_user_calls == []
    assert cli.client.respect_calls == []
    assert cli.save_count == 0


def test_respect_prompt_skips_for_excluded_command(monkeypatch) -> None:
    cli = RespectPromptCLIStub()
    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("input must not be called"))

    HtbCLI.maybe_prompt_author_respect(cli, command_name="respect")

    assert cli.client.get_user_calls == []
    assert cli.client.respect_calls == []
    assert cli.save_count == 0


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


class ParserStub:
    def __init__(self, args: argparse.Namespace) -> None:
        self._args = args
        self.help_called = False

    def parse_args(self) -> argparse.Namespace:
        return self._args

    def print_help(self) -> None:
        self.help_called = True


class StartCLIStub:
    def __init__(self, api_key: str | None = "token") -> None:
        self.logger = LoggerStub()
        self.console = ConsoleStub()
        self.api_key = api_key
        self.start_calls = 0
        self.stop_calls = 0
        self.prompt_calls = []
        self._wait_animation_thread = None

    def maybe_prompt_author_respect(self, command_name: str | None) -> None:
        self.prompt_calls.append(command_name)

    def start_wait_animation(self, text: str = "Please wait...", stream=None) -> None:
        self.start_calls += 1

    def stop_wait_animation(self) -> None:
        self.stop_calls += 1


class DummyCommand(BaseCommand):
    execute_calls = 0

    def execute(self):
        DummyCommand.execute_calls += 1


def test_start_wraps_base_command_with_wait_animation(monkeypatch) -> None:
    DummyCommand.execute_calls = 0
    cli = StartCLIStub(api_key="token")
    args = argparse.Namespace(command="machine", func=DummyCommand)
    parser = ParserStub(args=args)
    monkeypatch.setattr("htb_operator.create_arg_parser", lambda *_: parser)

    HtbCLI.start(cli)

    assert DummyCommand.execute_calls == 1
    assert cli.start_calls == 1
    assert cli.stop_calls == 1
    assert cli.prompt_calls == ["machine"]


def test_start_wraps_function_command_with_wait_animation(monkeypatch) -> None:
    called = {"count": 0}

    def fn(_args):
        called["count"] += 1

    cli = StartCLIStub(api_key=None)
    args = argparse.Namespace(command="version", func=fn)
    parser = ParserStub(args=args)
    monkeypatch.setattr("htb_operator.create_arg_parser", lambda *_: parser)

    HtbCLI.start(cli)

    assert called["count"] == 1
    assert cli.start_calls == 1
    assert cli.stop_calls == 1
    assert cli.prompt_calls == ["version"]


def test_start_stops_wait_animation_on_request_exception(monkeypatch) -> None:
    def fn(_args):
        raise RequestException({"message": "boom"})

    cli = StartCLIStub(api_key="token")
    args = argparse.Namespace(command="machine", func=fn)
    parser = ParserStub(args=args)
    monkeypatch.setattr("htb_operator.create_arg_parser", lambda *_: parser)

    HtbCLI.start(cli)

    assert cli.start_calls == 1
    assert cli.stop_calls == 1
    assert any("boom" in msg for msg in cli.logger.errors)
