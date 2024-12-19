import argparse
import ctypes
import itertools
import os
import subprocess
import sys
import threading
import time
from logging import Logger

from colorama import Fore, Style
from rich.console import Console

from htbapi import HTBClient

IS_WINDOWS: bool = sys.platform.startswith("win")
IS_ROOT_OR_ADMIN: bool =  ((not IS_WINDOWS and os.getuid() == 0) or
                           (IS_WINDOWS and ctypes.windll.shell32.IsUserAnAdmin()))

class InsufficientPermissions(Exception):
    pass

class BaseCommand(object):
    # noinspection PyUnresolvedReferences
    htb_cli: "HtbCLI"
    args: argparse.Namespace
    stop_animation: threading.Event
    logger: Logger
    client: HTBClient
    console: Console

    # noinspection PyUnresolvedReferences
    def __init__(self,
                 htb_cli: "HtbCLI",
                 args: argparse.Namespace):

        assert htb_cli is not None
        assert args is not None and (isinstance(args, argparse.Namespace))

        self.htb_cli = htb_cli
        self.args = args
        self.stop_animation = threading.Event()
        self.logger = self.htb_cli.logger
        self.client = self.htb_cli.client if hasattr(self.htb_cli, "client") else None
        self.console = self.htb_cli.console


    def animate_spinner(self, text: str, title: str):
        spinner = itertools.cycle(['|', '/', '-', '\\'])  # Rotating cross

        while not self.stop_animation.is_set():
            print(f'\r{Fore.CYAN}{title}: {text}{next(spinner)}{Style.RESET_ALL}', end="", flush=True)
            time.sleep(0.1)

    # Need to override
    def execute(self):
        raise NotImplementedError


    def switch_to_root(self, callback_execute_after_root_finished=None):
        """Switch to root/administrator. No effect if the app has been started as root/administrator."""
        if IS_ROOT_OR_ADMIN:
            return None

        self.logger.warning(f'{Fore.LIGHTYELLOW_EX}Some operations need root/admin permissions. Switch to root/administrator.{Style.RESET_ALL}')

        env = os.environ.copy()
        if IS_WINDOWS:
            env["HTB_TERMINAL_STORE_DIR"] = os.path.join(os.getenv("APPDATA"), self.htb_cli.package_name)
        else:
            env["HTB_TERMINAL_STORE_DIR"] = os.path.join(os.path.expanduser("~"), ".config", self.htb_cli.package_name)

        if IS_WINDOWS:
            try:
                current_directory = os.getcwd()
                ctypes.windll.shell32.ShellExecuteW(
                    ctypes.windll.kernel32.GetConsoleWindow(),
                    "runas",
                   "cmd.exe",
                    f'/K "{sys.executable} {os.path.join(current_directory, sys.argv[0])} {" ".join(sys.argv[1:])}"',
                    None,
                    1
                 )
            except Exception as e:
                self.logger.error(f"{Fore.RED}Error while requesting UAC: {e}{Style.RESET_ALL}")
                sys.exit(0)
        else:
            subprocess.run(args=['sudo', '-E', sys.executable] + sys.argv,
                           env=env,
                           text=True,
                           stderr=sys.stderr,
                           stdout=sys.stdout,
                           stdin=sys.stdin)

        if callback_execute_after_root_finished:
            callback_execute_after_root_finished()
        sys.exit(0)