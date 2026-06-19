from __future__ import annotations

import argparse
import importlib
import sys
import types
from pathlib import Path
from datetime import datetime, timezone
from types import SimpleNamespace

# Prevent executing command/__init__.py (side effects) by registering a dummy
# package with a correct __path__ and importing submodules via importlib.
if "command" not in sys.modules:
    pkg = types.ModuleType("command")
    pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "command")]
    sys.modules["command"] = pkg

badge_mod = importlib.import_module("command.badge")
certificate_mod = importlib.import_module("command.certificate")
prolabs_mod = importlib.import_module("command.prolabs")
pwnbox_mod = importlib.import_module("command.pwnbox")
season_mod = importlib.import_module("command.season")
sherlock_mod = importlib.import_module("command.sherlock")

BadgeCommand = badge_mod.BadgeCommand
CertificateCommand = certificate_mod.CertificateCommand
ProlabsCommand = prolabs_mod.ProlabsCommand
PwnBoxCommand = pwnbox_mod.PwnBoxCommand
SeasonCommand = season_mod.SeasonCommand
SherlockCommand = sherlock_mod.SherlockCommand

# Load Request-/PwnBox exceptions without executing htbapi/__init__.py
try:
    from htbapi.exception.errors import NoPwnBoxActiveException, RequestException  # type: ignore
except Exception:
    if "htbapi" not in sys.modules:
        htbapi_pkg = types.ModuleType("htbapi")
        htbapi_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "htbapi")]
        sys.modules["htbapi"] = htbapi_pkg
    errors_mod = importlib.import_module("htbapi.exception.errors")
    NoPwnBoxActiveException = getattr(errors_mod, "NoPwnBoxActiveException", Exception)
    RequestException = getattr(errors_mod, "RequestException", Exception)


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


class CLIStub:
    def __init__(self, client=None) -> None:
        self.logger = LoggerStub()
        self.console = ConsoleStub()
        self.client = client if client is not None else SimpleNamespace()


class BadgeCategoryStub:
    def __init__(self, name: str) -> None:
        self.name = name

    def to_dict(self) -> dict:
        return {"name": self.name}


class CertificateStub:
    def __init__(self, cert_id: int, name: str, downloaded: bool) -> None:
        self.cert_id = cert_id
        self.name = name
        self.has_downloaded_cert = downloaded
        self.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)


class ProlabStub:
    def __init__(self, submit_result: tuple[bool, str]) -> None:
        self.submit_result = submit_result
        self.submitted_flags = []

    def submit_flag(self, flag: str) -> tuple[bool, str]:
        self.submitted_flags.append(flag)
        return self.submit_result

    def to_dict(self) -> dict:
        return {"name": "Example Prolab"}


class ProlabMilestoneStub:
    def __init__(self, percent: int, text: str, reached: bool) -> None:
        self.percent = percent
        self.text = text
        self.is_milestone_reached = reached
        self.rarity = 5
        self.description = f"{text} description"


class ProlabProgressStub:
    def __init__(self) -> None:
        self.ownership = 42.5
        self.ownership_required_for_certification = 70
        self.milestones = [
            ProlabMilestoneStub(25, "Quarter", True),
            ProlabMilestoneStub(50, "Half", False),
        ]


class ProlabChangeLogStub:
    def __init__(self, created_at: datetime, log_type: str, title: str) -> None:
        self.created_at = created_at
        self.type = log_type
        self.title = title
        self.description = f"{title} description"
        self.user = SimpleNamespace(name="alice")


class ProlabDetailsStub:
    def __init__(self) -> None:
        self.name = "Example Prolab"

    @staticmethod
    def get_flags():
        return [SimpleNamespace(id=1, title="Flag 1", points=10, owned=True)]

    @staticmethod
    def get_machines():
        return [SimpleNamespace(id=11, name="box1", os="Linux")]

    @staticmethod
    def get_progress():
        return ProlabProgressStub()

    @staticmethod
    def get_changelogs():
        return [
            ProlabChangeLogStub(datetime(2025, 1, 1, tzinfo=timezone.utc), "update", "Updated VPN"),
            ProlabChangeLogStub(datetime(2024, 12, 31, tzinfo=timezone.utc), "add", "Added host"),
        ]

    @staticmethod
    def get_reset_status():
        return None, datetime(2024, 10, 1, 12, 0, 0, tzinfo=timezone.utc)


class SherlockInfoStub:
    def __init__(self, name: str, state: str) -> None:
        self.name = name
        self.state = state

    def to_dict(self) -> dict:
        return {"name": self.name, "state": self.state}


class SeasonListStub:
    def __init__(self, season_id: int, name: str, active: bool = False) -> None:
        self.id = season_id
        self.name = name
        self.active = active
        self.start_date = datetime(2024, 1, season_id, tzinfo=timezone.utc)
        self.end_date = None

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}


def test_badge_execute_missing_command_logs_error() -> None:
    cli = CLIStub()
    BadgeCommand(htb_cli=cli, args=argparse.Namespace()).execute()

    assert any("missing" in msg.lower() for msg in cli.logger.errors)


def test_badge_list_filters_categories_and_warns_invalid(monkeypatch) -> None:
    class ClientStub:
        def __init__(self) -> None:
            self.calls = []

        def get_badges(self, user_id=None, username=None, remove_obtained_badges=False):
            self.calls.append((user_id, username, remove_obtained_badges))
            return [BadgeCategoryStub("Web"), BadgeCategoryStub("Crypto")]

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(badge="list", user_id=7, username="alice", open=True, category="web,invalid")

    monkeypatch.setattr("command.badge.create_table_badge_list", lambda badge_categories: badge_categories)
    BadgeCommand(htb_cli=cli, args=args).execute()

    assert cli.client.calls == [(7, "alice", True)]
    assert cli.console.printed == [[{"name": "Web"}]]
    assert any("invalid" in msg.lower() for msg in cli.logger.warnings)


def test_badge_execute_unknown_command_logs_error() -> None:
    cli = CLIStub()
    BadgeCommand(htb_cli=cli, args=argparse.Namespace(badge="unknown")).execute()

    assert any("unknown command" in msg.lower() for msg in cli.logger.errors)


def test_certificate_execute_without_options_logs_error() -> None:
    cli = CLIStub()
    CertificateCommand(htb_cli=cli, args=argparse.Namespace()).execute()

    assert any("no options" in msg.lower() for msg in cli.logger.errors)


def test_certificate_list_without_results_warns() -> None:
    class ClientStub:
        @staticmethod
        def get_prolab_certificate_list():
            return []

    cli = CLIStub(client=ClientStub())
    CertificateCommand(htb_cli=cli, args=argparse.Namespace(list=True)).execute()

    assert any("no certificates obtained" in msg.lower() for msg in cli.logger.warnings)


def test_certificate_list_prints_panel_when_results_exist() -> None:
    class ClientStub:
        @staticmethod
        def get_prolab_certificate_list():
            return [CertificateStub(11, "Rastalabs", True)]

    cli = CLIStub(client=ClientStub())
    CertificateCommand(htb_cli=cli, args=argparse.Namespace(list=True)).execute()

    assert len(cli.console.printed) == 1


def test_certificate_download_success_logs_info() -> None:
    class ClientStub:
        @staticmethod
        def download_prolab_certificate(_id, path=None):
            return "/tmp/certificate.pdf"

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(certificate="download", id=17, filename="certificate.pdf", list=False)
    CertificateCommand(htb_cli=cli, args=args).execute()

    assert any("successfully downloaded" in msg.lower() for msg in cli.logger.infos)


def test_certificate_download_request_exception_logs_error() -> None:
    class ClientStub:
        @staticmethod
        def download_prolab_certificate(_id, path=None):
            raise RequestException("download failed")

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(certificate="download", id=17, filename="certificate.pdf", list=False)
    CertificateCommand(htb_cli=cli, args=args).execute()

    assert any("error:" in msg.lower() for msg in cli.logger.errors)


def test_prolabs_checks_require_id_or_name_for_info() -> None:
    cli = CLIStub()
    cmd = ProlabsCommand(htb_cli=cli, args=argparse.Namespace(prolabs="info", id=None, name=None, flag=None))

    assert cmd.checks() is False
    assert any("id or name must be specified" in msg.lower() for msg in cli.logger.errors)


def test_prolabs_checks_require_flag_for_submit() -> None:
    cli = CLIStub()
    cmd = ProlabsCommand(htb_cli=cli, args=argparse.Namespace(prolabs="submit", id=2, name=None, flag=None))

    assert cmd.checks() is False
    assert any("flag must be specified" in msg.lower() for msg in cli.logger.errors)


def test_prolabs_submit_success_logs_info() -> None:
    prolab = ProlabStub((True, "accepted"))

    class ClientStub:
        @staticmethod
        def get_prolab(prolab_id=None, prolab_name=None):
            return prolab

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(prolabs="submit", id=8, name=None, flag="HTB{ok}")
    ProlabsCommand(htb_cli=cli, args=args).submit()

    assert prolab.submitted_flags == ["HTB{ok}"]
    assert any("accepted" in msg.lower() for msg in cli.logger.infos)


def test_prolabs_submit_failure_logs_error() -> None:
    prolab = ProlabStub((False, "wrong flag"))

    class ClientStub:
        @staticmethod
        def get_prolab(prolab_id=None, prolab_name=None):
            return prolab

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(prolabs="submit", id=8, name=None, flag="HTB{bad}")
    ProlabsCommand(htb_cli=cli, args=args).submit()

    assert prolab.submitted_flags == ["HTB{bad}"]
    assert any("wrong flag" in msg.lower() for msg in cli.logger.errors)


def test_prolabs_submit_logs_error_when_prolab_missing() -> None:
    class ClientStub:
        @staticmethod
        def get_prolab(prolab_id=None, prolab_name=None):
            return None

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(prolabs="submit", id=9, name=None, flag="HTB{x}")
    ProlabsCommand(htb_cli=cli, args=args).submit()

    assert any('id "9"' in msg.lower() for msg in cli.logger.errors)


def test_prolabs_execute_unknown_command_logs_error() -> None:
    cli = CLIStub()
    ProlabsCommand(htb_cli=cli, args=argparse.Namespace(prolabs="unknown", flag=None)).execute()

    assert any("unknown command" in msg.lower() for msg in cli.logger.errors)


def test_prolabs_checks_require_id_or_name_for_progress() -> None:
    cli = CLIStub()
    args = argparse.Namespace(prolabs="progress", id=None, name=None, flag=None, limit=20)
    cmd = ProlabsCommand(htb_cli=cli, args=args)

    assert cmd.checks() is False
    assert any("id or name must be specified" in msg.lower() for msg in cli.logger.errors)


def test_prolabs_flags_and_machines_print_tables() -> None:
    class ClientStub:
        @staticmethod
        def get_prolab(prolab_id=None, prolab_name=None):
            return ProlabDetailsStub()

    cli = CLIStub(client=ClientStub())
    flags_args = argparse.Namespace(prolabs="flags", id=1, name=None, flag=None, limit=20)
    machines_args = argparse.Namespace(prolabs="machines", id=1, name=None, flag=None, limit=20)

    ProlabsCommand(htb_cli=cli, args=flags_args).execute()
    ProlabsCommand(htb_cli=cli, args=machines_args).execute()

    assert len(cli.console.printed) == 2


def test_prolabs_progress_warns_when_missing() -> None:
    class MissingProgressProlabStub(ProlabDetailsStub):
        @staticmethod
        def get_progress():
            return None

    class ClientStub:
        @staticmethod
        def get_prolab(prolab_id=None, prolab_name=None):
            return MissingProgressProlabStub()

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(prolabs="progress", id=7, name=None, flag=None, limit=20)
    ProlabsCommand(htb_cli=cli, args=args).execute()

    assert any("no progress information available" in msg.lower() for msg in cli.logger.warnings)


def test_prolabs_progress_prints_group_panel() -> None:
    class ClientStub:
        @staticmethod
        def get_prolab(prolab_id=None, prolab_name=None):
            return ProlabDetailsStub()

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(prolabs="progress", id=7, name=None, flag=None, limit=20)
    ProlabsCommand(htb_cli=cli, args=args).execute()

    assert len(cli.console.printed) == 1


def test_prolabs_changelog_warns_when_empty() -> None:
    class EmptyChangelogProlabStub(ProlabDetailsStub):
        @staticmethod
        def get_changelogs():
            return []

    class ClientStub:
        @staticmethod
        def get_prolab(prolab_id=None, prolab_name=None):
            return EmptyChangelogProlabStub()

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(prolabs="changelog", id=7, name=None, flag=None, limit=20)
    ProlabsCommand(htb_cli=cli, args=args).execute()

    assert any("no changelog entries found" in msg.lower() for msg in cli.logger.warnings)


def test_prolabs_reset_status_prints_panel() -> None:
    class ClientStub:
        @staticmethod
        def get_prolab(prolab_id=None, prolab_name=None):
            return ProlabDetailsStub()

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(prolabs="reset-status", id=7, name=None, flag=None, limit=20)
    ProlabsCommand(htb_cli=cli, args=args).execute()

    assert len(cli.console.printed) == 1


def test_sherlock_list_all_fetches_active_and_retired(monkeypatch) -> None:
    class ClientStub:
        def __init__(self) -> None:
            self.calls = []

        def get_sherlocks(self, only_active=False, only_retired=False, filter_sherlock_category=None):
            self.calls.append((only_active, only_retired, filter_sherlock_category))
            if only_active:
                return [SherlockInfoStub("Alpha", "active")]
            return [SherlockInfoStub("Bravo", "retired")]

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(sherlock="list", active=False, retired=False, all=True, filter_category=None)

    monkeypatch.setattr(
        "command.sherlock.create_sherlock_list_group_by_retired_panel",
        lambda sherlock_info: sherlock_info,
    )
    SherlockCommand(htb_cli=cli, args=args).execute()

    assert len(cli.client.calls) == 2
    assert cli.client.calls[0][:2] == (True, False)
    assert cli.client.calls[1][:2] == (False, True)
    assert [x["name"] for x in cli.console.printed[0]] == ["Alpha", "Bravo"]


def test_sherlock_list_invalid_filter_warns(monkeypatch) -> None:
    class ClientStub:
        def __init__(self) -> None:
            self.calls = []

        @staticmethod
        def get_sherlock_categories():
            return [SimpleNamespace(name="Web")]

        def get_sherlocks(self, only_active=False, only_retired=False, filter_sherlock_category=None):
            self.calls.append((only_active, only_retired, filter_sherlock_category))
            return []

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(sherlock="list", active=False, retired=False, all=False, filter_category="web,invalid")

    monkeypatch.setattr(
        "command.sherlock.create_sherlock_list_group_by_retired_panel",
        lambda sherlock_info: sherlock_info,
    )
    SherlockCommand(htb_cli=cli, args=args).list()

    assert len(cli.client.calls) == 1
    assert cli.client.calls[0][0:2] == (True, False)
    assert [x.name for x in cli.client.calls[0][2]] == ["Web"]
    assert any("not a valid sherlock category" in msg.lower() for msg in cli.logger.warnings)


def test_sherlock_execute_unknown_command_logs_error() -> None:
    cli = CLIStub()
    SherlockCommand(htb_cli=cli, args=argparse.Namespace(sherlock="unknown")).execute()

    assert any("unknown command" in msg.lower() for msg in cli.logger.errors)


def test_season_checks_invalid_ids_logs_error() -> None:
    cli = CLIStub()
    args = argparse.Namespace(seasons="info", username="alice", ids="1,x")
    cmd = SeasonCommand(htb_cli=cli, args=args)

    assert cmd.checks(obj=SimpleNamespace(id=1)) is False
    assert any("only numbers are allowed" in msg.lower() for msg in cli.logger.errors)


def test_season_list_no_seasons_warns() -> None:
    class ClientStub:
        @staticmethod
        def get_season_list():
            return []

    cli = CLIStub(client=ClientStub())
    SeasonCommand(htb_cli=cli, args=argparse.Namespace(seasons="list")).list()

    assert any("no seasons found" in msg.lower() for msg in cli.logger.warnings)


def test_season_info_warns_when_filtered_ids_not_found() -> None:
    class ClientStub:
        @staticmethod
        def get_user(_username=None):
            return SimpleNamespace(id=42, name="alice")

        @staticmethod
        def get_season_list():
            return [SeasonListStub(1, "Season 1"), SeasonListStub(2, "Season 2")]

    cli = CLIStub(client=ClientStub())
    args = argparse.Namespace(seasons="info", username="alice", ids="9")
    SeasonCommand(htb_cli=cli, args=args).info()

    assert any("there are no season for id(s)" in msg.lower() for msg in cli.logger.warnings)


def test_season_print_machines_warns_when_empty() -> None:
    class ClientStub:
        @staticmethod
        def get_current_season_machines():
            return []

    cli = CLIStub(client=ClientStub())
    SeasonCommand(htb_cli=cli, args=argparse.Namespace(seasons="machine")).print_machines()

    assert any("no machines found" in msg.lower() for msg in cli.logger.warnings)


def test_season_execute_unknown_command_logs_error() -> None:
    cli = CLIStub()
    SeasonCommand(htb_cli=cli, args=argparse.Namespace(seasons="unknown")).execute()

    assert any("unknown command" in msg.lower() for msg in cli.logger.errors)


def test_pwnbox_get_status_handles_no_active_exception() -> None:
    class ClientStub:
        @staticmethod
        def get_pwnbox_status():
            raise NoPwnBoxActiveException("No active pwnbox")

    cli = CLIStub(client=ClientStub())
    cmd = PwnBoxCommand(htb_cli=cli, args=argparse.Namespace(pwnbox="status"))

    assert cmd._get_pwnbox_status() is None
    assert any("no active pwnbox" in msg.lower() for msg in cli.logger.errors)


def test_pwnbox_check_ssh_requires_sshpass(monkeypatch) -> None:
    cli = CLIStub()
    cmd = PwnBoxCommand(htb_cli=cli, args=argparse.Namespace(pwnbox="ssh"))

    monkeypatch.setattr("command.pwnbox.shutil.which", lambda exe: None if exe == "sshpass" else f"/usr/bin/{exe}")

    assert cmd.check(pwnbox_status=SimpleNamespace()) is False
    assert any("sshpass is not installed" in msg.lower() for msg in cli.logger.errors)


def test_pwnbox_execute_unknown_command_logs_error() -> None:
    cli = CLIStub()
    PwnBoxCommand(htb_cli=cli, args=argparse.Namespace(pwnbox="unknown")).execute()

    assert any("unknown command" in msg.lower() for msg in cli.logger.errors)
