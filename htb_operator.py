#!/usr/bin/env python3

import argparse
import configparser
import ctypes
import logging
import os
import sys
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
    def __init__(self, htb_http_request: Optional[BaseHtbHttpRequest] = None):
        self.package_name = 'htb-operator'
        self.config = configparser.ConfigParser()
        self.logger = setup_logger()
        self.api_key, self._api_base, self._user_agent = self.load_cli_config()
        self.console = Console()

        try:
            self.version = version(self.package_name)
        except PackageNotFoundError:
            self.version = "0.0.0.1"

        self.proxy = self.config["Proxy"] if "Proxy" in self.config else None

        if self.api_key is not None:
            if htb_http_request is None:
                htb_http_request = HtbHtbHttpRequest(app_token=self.api_key,
                                                     api_base=self._api_base,
                                                     user_agent=self._user_agent,
                                                     proxy=self.proxy)
            self.client = HTBClient(htb_http_request=htb_http_request)

    def get_base_store_dir(self) -> str:
        if sys.platform.startswith("win"):
            config_path = os.path.join(os.getenv("APPDATA"), self.package_name)
        else:
            # Only for Linux
            config_path = os.path.join(os.path.expanduser("~"), ".config", self.package_name)

        env_store_dir = os.environ.get("HTB_TERMINAL_STORE_DIR")
        return env_store_dir if env_store_dir else config_path

    def load_cli_config(self) -> [str, str, str]:
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
                if not (ismethod(args.func) or isfunction(args.func)) and issubclass(args.func, BaseCommand):
                    args.func(self, args).execute()
                else:
                    args.func(args)
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
