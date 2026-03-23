#!/usr/bin/env python3

import argparse
import configparser
import ctypes
import itertools
import logging
import os
import sys
import threading
import time
from argparse import ArgumentParser
from importlib.metadata import version, PackageNotFoundError
from inspect import isfunction, ismethod
from logging import Logger
from typing import Optional

from colorama import Fore, Style
from rich.console import Console

from command.base import BaseCommand, InsufficientPermissions
from console import *
from htbapi import HTBClient, RequestException, HtbHtbHttpRequest, BaseHtbHttpRequest

IS_WINDOWS: bool = sys.platform.startswith("win")
IS_ROOT_OR_ADMIN: bool =  ((not IS_WINDOWS and os.getuid() == 0) or
                           (IS_WINDOWS and ctypes.windll.shell32.IsUserAnAdmin()))

class HtbCLI:
    """Main class for the HTB-Command line interface"""
    AUTHOR_USERNAME = "user01337"
    RESPECT_PROMPT_DONE_KEY = "respect_prompt_done"
    PROMPT_EXCLUDED_COMMANDS = {"help", "init", "respect", "version"}

    class _OutputProxy:
        def __init__(self, wrapped, on_write):
            self._wrapped = wrapped
            self._on_write = on_write

        def write(self, data):
            if data:
                self._on_write()
            return self._wrapped.write(data)

        def flush(self):
            return self._wrapped.flush()

        def fileno(self):
            return self._wrapped.fileno()

        def isatty(self):
            return self._wrapped.isatty()

        def __getattr__(self, item):
            return getattr(self._wrapped, item)

    def __init__(self, htb_http_request: Optional[BaseHtbHttpRequest] = None):
        self.package_name = 'htb-operator'
        self.config = configparser.ConfigParser()
        self.logger = setup_logger()
        self.api_key, self._api_base, self._user_agent = self.load_cli_config()
        self.console = Console()
        self._wait_animation_stop: Optional[threading.Event] = None
        self._wait_animation_thread: Optional[threading.Thread] = None
        self._wait_animation_lock = threading.Lock()
        self._wait_animation_stream = sys.stdout
        self._wait_animation_last_len = 0

        try:
            self.version = version(self.package_name)
        except PackageNotFoundError:
            self.version = "0.0.0.1"

        self.proxy = self.config["Proxy"] if "Proxy" in self.config else {}

        # Migrate old verify_ssl location from Proxy section to HTB section
        if "Proxy" in self.config and "verify_ssl" in self.config["Proxy"]:
            if "HTB" not in self.config:
                self.config["HTB"] = {}
            self.config["HTB"]["verify_ssl"] = self.config["Proxy"]["verify_ssl"]
            del self.config["Proxy"]["verify_ssl"]
            self.save_config_file()

        if self.api_key is not None:
            if "HTB" in self.config and "verify_ssl" in self.config["HTB"]:
                verify_ssl = self.config["HTB"]["verify_ssl"].strip().lower() == "true"
            else:
                verify_ssl = True

            if htb_http_request is None:
                htb_http_request = HtbHtbHttpRequest(app_token=self.api_key,
                                                     api_base=self._api_base,
                                                     user_agent=self._user_agent,
                                                     proxy=self.proxy if self.proxy else None,
                                                     verify_ssl=verify_ssl)
            self.client = HTBClient(htb_http_request=htb_http_request)

    def _animate_wait(self, text: str) -> None:
        spinner = itertools.cycle(['|', '/', '-', '\\'])
        while self._wait_animation_stop is not None and not self._wait_animation_stop.is_set():
            frame = f"{text} {next(spinner)}"
            padding = max(self._wait_animation_last_len - len(frame), 0)
            self._wait_animation_stream.write(f'\r{frame}{" " * padding}')
            self._wait_animation_stream.flush()
            self._wait_animation_last_len = len(frame)
            time.sleep(0.1)

    def start_wait_animation(self, text: str = "Please wait...", stream=None) -> None:
        with self._wait_animation_lock:
            if self._wait_animation_thread is not None and self._wait_animation_thread.is_alive():
                return
            self._wait_animation_stream = stream if stream is not None else sys.stdout
            self._wait_animation_stop = threading.Event()
            self._wait_animation_last_len = 0
            self._wait_animation_thread = threading.Thread(target=self._animate_wait, args=(text,), daemon=True)
            self._wait_animation_thread.start()

    def stop_wait_animation(self) -> None:
        with self._wait_animation_lock:
            stop_event = self._wait_animation_stop
            animation_thread = self._wait_animation_thread
            wait_stream = self._wait_animation_stream
            self._wait_animation_stop = None
            self._wait_animation_thread = None

        had_animation = stop_event is not None or (animation_thread is not None and animation_thread.is_alive())
        if stop_event is not None:
            stop_event.set()
        if animation_thread is not None and animation_thread.is_alive():
            animation_thread.join()

        if not had_animation:
            return

        # Clear spinner line after command output is ready.
        wait_stream.write(f'\r{" " * self._wait_animation_last_len}\r')
        wait_stream.flush()
        self._wait_animation_last_len = 0

    def get_base_store_dir(self) -> str:
        if sys.platform.startswith("win"):
            config_path = os.path.join(os.getenv("APPDATA"), self.package_name)
        else:
            # Only for Linux
            config_path = os.path.join(os.path.expanduser("~"), ".config", self.package_name)

        env_store_dir = os.environ.get("HTB_TERMINAL_STORE_DIR")
        return env_store_dir if env_store_dir else config_path

    def load_cli_config(self) -> tuple[str|None, str|None, str|None]:
        """Loads the API key from the config file if it exists."""
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            self.config.read(config_path)
            return (self.config["HTB"].get("api_key"),
                    self.config["HTB"].get("api_base_url"),
                    self.config["HTB"].get("user_agent"))

        return None, None, None


    def get_config_path(self) -> str:
        """Returns the path to the config file."""
        return os.path.join(self.get_base_store_dir(), "config.ini")

    def save_config_file(self):
        """Save the config file"""
        config_path = self.get_config_path()
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, "w") as configfile:
            self.config.write(configfile)

    def maybe_prompt_author_respect(self, command_name: Optional[str]) -> None:
        """Prompt the user to give respect to the author of htb-operator on HTB.

        This function checks if the user has already given respect and if the command
        is excluded from prompting. If not, it prompts the user to give respect.
        """
        if self.api_key is None or not hasattr(self, "client"):
            return

        if command_name in HtbCLI.PROMPT_EXCLUDED_COMMANDS:
            return

        if self.config.getboolean("HTB", HtbCLI.RESPECT_PROMPT_DONE_KEY, fallback=False):
            return

        answer = input("Would you like to give htb-operator's author on HTB a respect? [y/N]: ").strip().lower()

        if "HTB" not in self.config:
            self.config["HTB"] = {}
        self.config["HTB"][HtbCLI.RESPECT_PROMPT_DONE_KEY] = str(True)
        self.save_config_file()

        if answer in {"y", "yes"}:
            user = self.client.get_user(HtbCLI.AUTHOR_USERNAME)
            self.client.give_user_respect(user_id=user.id)
            print("Thank you very much for your respect!")

    def start(self):
        if IS_ROOT_OR_ADMIN:
            self.logger.warning(f'{Fore.LIGHTYELLOW_EX}App is running as {"Administrator" if IS_WINDOWS else "root"}{Style.RESET_ALL}')

        parser: ArgumentParser = create_arg_parser(self)
        args: argparse.Namespace = parser.parse_args()
        init = self.api_key is not None

        if args.command is None or args.command == "help":
            parser.print_help()
        elif not init and args.command not in ["version", "init"]:
            print(f"{Fore.RED}HTB-Operator needs to be initialized. Use the \"init\" command.{Style.RESET_ALL}", file=sys.stderr)
        else:
            try:
                self.maybe_prompt_author_respect(command_name=args.command)
                original_stdout = sys.stdout
                original_stderr = sys.stderr
                stdout_proxy = HtbCLI._OutputProxy(original_stdout, self.stop_wait_animation)
                stderr_proxy = HtbCLI._OutputProxy(original_stderr, self.stop_wait_animation)
                old_handler_streams = []

                for handler in getattr(self.logger, "handlers", []):
                    if not hasattr(handler, "stream"):
                        continue
                    old_handler_streams.append((handler, handler.stream))
                    if handler.stream is original_stderr:
                        handler.stream = stderr_proxy
                    elif handler.stream is original_stdout:
                        handler.stream = stdout_proxy

                self.start_wait_animation(stream=original_stdout)
                sys.stdout = stdout_proxy
                sys.stderr = stderr_proxy
                try:
                    if not (ismethod(args.func) or isfunction(args.func)) and issubclass(args.func, BaseCommand):
                        args.func(self, args).execute()
                    else:
                        args.func(args)
                finally:
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    for handler, stream in old_handler_streams:
                        handler.stream = stream
                    self.stop_wait_animation()
            except RequestException as e:
                if len(e.args) > 0 and "message" in e.args[0]:
                    self.logger.error(f'{Fore.RED}{e.args[0]["message"]}{Style.RESET_ALL}')
                else:
                    self.logger.error(f'{Fore.RED}{e}{Style.RESET_ALL}')
                return None
            except InsufficientPermissions as e:
                pass
        print()

class CustomFormatter(logging.Formatter):
    """Custom logging formatter with color."""
    def format(self, record):
        level = record.levelname
        if level == "INFO":
            prefix = f"{Fore.GREEN}[+]{Style.RESET_ALL}"
        elif level == "ERROR":
            prefix = f"{Fore.RED}[-]{Style.RESET_ALL}"
        elif level == "WARNING":
            prefix = f"{Fore.YELLOW}[*]{Style.RESET_ALL}"
        else:
            prefix = ""
        return f"{prefix} {record.getMessage()}"

def setup_logger() -> Logger:
    """Sets up a logger with colored output."""
    logger = logging.getLogger("HtbCLI")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)

    return logger

def main():
    cli = HtbCLI()
    try:
        cli.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'{Fore.RED}Error: {e}{Style.RESET_ALL}', file=sys.stderr)

if __name__ == '__main__':
    main()
