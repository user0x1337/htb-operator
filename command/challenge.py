import argparse
import hashlib
import os
import threading
import zipfile
from typing import Optional, List

from colorama import Fore, Style

from command.base import BaseCommand
from console import create_challenge_info_panel, create_table_challenge_list
from htbapi import ChallengeInfo, RequestException, UnknownDirectoryException, ChallengeList, Category

DEFAULT_HTB_DOWNLOAD_PASSWORD = "hackthebox"

class ChallengeCommand(BaseCommand):
    challenge_command: Optional[str]
    instance_command: Optional[str]
    challenge_id: Optional[int]
    challenge_name: Optional[str]
    flag: Optional[str]
    difficulty: Optional[int]

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        self.challenge_command = args.challenge if hasattr(args, "challenge") else None
        self.challenge_id = args.id if hasattr(args, "id") else None
        self.challenge_name = args.name if hasattr(args, "name") else None
        self.flag = args.flag if hasattr(args, "flag") else None
        self.difficulty = args.difficulty if hasattr(args, "difficulty") else None
        self.instance_command = args.instance if hasattr(args, "instance") else None


    def submit(self):
        """Submit the challenge flag."""
        if self.challenge_id is None and self.challenge_name is None:
            self.logger.error(
                f"{Fore.RED}ID or Name must be specified. Use --help for more information.{Style.RESET_ALL}")
            return None

        if self.flag is None:
            self.logger.error(f"{Fore.RED}A flag must be specified.{Style.RESET_ALL}")
            return None

        if self.difficulty is None:
            self.logger.error(f"{Fore.RED}A difficulty rating must be specified{Style.RESET_ALL}")
            return None

        if type(self.difficulty) != int or self.difficulty < 0 or self.difficulty > 10:
            self.logger.error(f"{Fore.RED}The difficulty rating must be an integer between 1 and 10.{Style.RESET_ALL}")
            return None

        challenge_info: ChallengeInfo = self.client.get_challenge(challenge_id_or_name=self.challenge_id if self.challenge_id is not None else self.challenge_name)
        if challenge_info is None:
            self.logger.error(f'{Fore.RED}Challenge not found for ID/Name "{self.challenge_id if self.challenge_id is not None else self.challenge_name}"{Style.RESET_ALL}')
            return None

        try:
            res: bool = challenge_info.submit(flag=self.flag, difficulty=self.difficulty)
            if not res:
                self.logger.error(
                    f'{Fore.RED}Incorrect flag for challenge "{challenge_info.name}". Flag: {self.flag}{Style.RESET_ALL}')
            else:
                self.logger.info(f'{Fore.GREEN}Flag accepted.{Style.RESET_ALL}')
        except RequestException as e:
            self.logger.error(f'{Fore.RED}Error: {e.args[0]["message"]}{Style.RESET_ALL}')


    def download(self):
        """Download the challenge"""
        if self.challenge_id is None and self.challenge_name is None:
            self.logger.error(
                f"{Fore.RED}ID or Name must be specified. Use --help for more information.{Style.RESET_ALL}")
            return None

        challenge_id_or_name = self.challenge_id if self.challenge_id else self.challenge_name
        challenge_download_info: ChallengeInfo = self.client.get_challenge(
            challenge_id_or_name=challenge_id_or_name)
        if not challenge_download_info.downloadable:
            self.logger.error(
                f'{Fore.RED}Challenge "{challenge_download_info.name}" does not provide any downloads.{Style.RESET_ALL}')
            return None


        animation_thread = threading.Thread(target=self.animate_spinner,
                                            args=("Downloading...", challenge_download_info.name))
        animation_thread.start()
        try:
            filepath = challenge_download_info.download(path=self.args.path)
        except RequestException as e:
            self.logger.error(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            return None
        except UnknownDirectoryException as e:
            self.logger.error(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            return None
        finally:
            self.stop_animation.set()
            animation_thread.join()

        if filepath is None:
            return None

        print(
            f'\r{Fore.CYAN}[+] Challenge "{challenge_download_info.name}": Download completed. Stored in {filepath}. Size: {os.path.getsize(filepath) // 1024} KB. Start integrity check.{Style.RESET_ALL}')
        with open(filepath, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        self.logger.info(
            f'{Fore.CYAN}Challenge "{challenge_download_info.name}": HTB hash = {challenge_download_info.download_sha256} | File hash = {file_hash}{Style.RESET_ALL}')
        if file_hash != challenge_download_info.download_sha256:
            self.logger.info(
                f'{Fore.RED}[ERROR] Challenge "{challenge_download_info.name}": Integrity check failed. Hash provided by htb ({challenge_download_info.download_sha256}) does not match the file hash ({file_hash}). File is NOT removed. Be careful. {Style.RESET_ALL}\n')
        else:
            self.logger.info(
                f'{Fore.GREEN}Challenge "{challenge_download_info.name}": Integrity check passed. ZIP password: {Style.RESET_ALL}{Fore.MAGENTA}{DEFAULT_HTB_DOWNLOAD_PASSWORD}{Style.RESET_ALL}')
            self.logger.info(f'{Fore.GREEN}Good luck solving this challenge.{Style.RESET_ALL}')

        if self.args.unzip:
            with zipfile.ZipFile(filepath, "r") as zip_ref:
                zip_ref.extractall(path=os.path.dirname(filepath), pwd=DEFAULT_HTB_DOWNLOAD_PASSWORD.encode("utf8"))
            self.logger.info(f'{Fore.GREEN}Zip file extracted to {os.path.dirname(filepath)}')

        # Need to be the last step inside the download branch
        if self.args.start_instance and challenge_download_info.docker:
            self.start_instance(challenge=challenge_download_info)


    def print_info(self):
        """Print the challenge info"""
        if self.challenge_id is None and self.challenge_name is None:
            self.logger.error("ID or Name must be specified. Use --help for more information.")
            return None

        challenge_id_or_name = self.challenge_id if self.challenge_id else self.challenge_name
        challenge_info: ChallengeInfo = self.client.get_challenge(challenge_id_or_name=challenge_id_or_name)
        table = create_challenge_info_panel(channel_info=challenge_info.to_dict())
        self.console.print(table)

    def _get_filter_category_list(self, category_dict:dict):
        cat_filter_list = []
        if self.args.category:
            cat_list = self.args.category.split(',')
            all_cats_invalid = True
            for cat in cat_list:
                if cat not in category_dict.values():
                    self.logger.warning(
                        f'{Fore.LIGHTYELLOW_EX}Category "{self.args.category}" is not a valid HTB category.{Style.RESET_ALL}')
                else:
                    all_cats_invalid = False

            if all_cats_invalid:
                return None

            for cat in cat_list:
                filter_category_id = next((key for key, value in category_dict.items() if value == cat), None)
                cat_filter_list.append(filter_category_id)
        return cat_filter_list

    def list_challenges(self):
        """List all challenges"""
        unsolved = None
        if self.args.unsolved:
            unsolved = self.args.unsolved
        elif self.args.solved:
            unsolved = not self.args.solved

        # Mapping between category-id and category_name. Challenge returns only the id.
        categories: List[Category] = self.client.get_challenge_categories_list()
        category_dict = {x.id: x.name for x in categories}

        filter_category_id = None
        cat_filter_list = self._get_filter_category_list(category_dict)
        challenge_list: List[ChallengeList] = self.client.get_challenge_list(retired=self.args.retired,
                                                                             unsolved=unsolved,
                                                                             filter_todo=self.args.todo,
                                                                             filter_category_list=cat_filter_list,
                                                                             filter_difficulty=self.args.difficulty)

        self.console.print((create_table_challenge_list(challenge_list=sorted([x.to_dict() for x in challenge_list], key=lambda x: x["difficulty_num"]), category_dict=category_dict)))


    def start_instance(self, challenge: ChallengeInfo):
        """Start an instance"""
        if challenge.docker_ip is not None and len(challenge.docker_ip) > 0:
            self.logger.warning(f"{Fore.LIGHTYELLOW_EX}Instance already started: "
                                f"{challenge.docker_ip}, Port(s): {",".join(str(x) for x in challenge.docker_ports)}"
                                f"{Style.RESET_ALL}")
            return None

        animation_thread = threading.Thread(target=self.animate_spinner,
                                            args=("Starting instance...", challenge.name))
        animation_thread.start()
        try:
            # Start instance if and only if it is already started.
            msg = challenge.start_instance()
            while challenge.docker_ip is None:
                challenge: ChallengeInfo = self.client.get_challenge(challenge_id_or_name=challenge.id)
        finally:
            self.stop_animation.set()
            animation_thread.join()

        if "Created" in msg:
            # Use print here because of the threading spinner. Otherwise, the row will not be overwritten
            self.logger.info(f'\r{Fore.GREEN}[+] "{challenge.name}": {msg.ljust(60)}{Style.RESET_ALL}')
            ports = ",".join(str(x) for x in challenge.docker_ports)
            self.logger.info(f"{Fore.GREEN}IP: {challenge.docker_ip}, Port(s): {ports}{Style.RESET_ALL}")
        else:
            # Use print here because of the threading spinner. Otherwise, the row will not be overwritten
            self.logger.error(f'\r{Fore.RED}"{challenge.name}": {msg}{Style.RESET_ALL}')


    def stop_instance(self, challenge: ChallengeInfo):
        """Stop an instance"""
        if challenge.docker_ip is None or len(challenge.docker_ip) == 0:
            self.logger.warning(f"{Fore.LIGHTYELLOW_EX}Instance is not running.{Style.RESET_ALL}")
            return None

        self.logger.warning(f'{Fore.LIGHTYELLOW_EX}"{challenge.name}": Stopping instance...{Style.RESET_ALL}')
        msg = challenge.stop_instance()
        if "Stopped" in msg:
            # Use print here because of the threading spinner. Otherwise, the row will not be overwritten
            self.logger.info(f'{Fore.GREEN}"{challenge.name}": {msg}{Style.RESET_ALL}')
        else:
            # Use print here because of the threading spinner. Otherwise, the row will not be overwritten
            self.logger.error(f'{Fore.RED}"{challenge.name}": {msg}{Style.RESET_ALL}')

    def status_instance(self, challenge: ChallengeInfo):
        """status instance"""
        if challenge.docker_ip is not None and len(challenge.docker_ip) > 0:
            self.logger.info(f"{Fore.GREEN}Instance already started: "
                             f"{challenge.docker_ip}, Port(s): {",".join(str(x) for x in challenge.docker_ports)}"
                             f"{Style.RESET_ALL}")
        else:
            self.logger.warning(f"{Fore.LIGHTYELLOW_EX}Instance ist not running.{Style.RESET_ALL}")


    def handle_instance(self):
        """Handle instances"""
        if self.challenge_id is None and self.challenge_name is None:
            self.logger.error(f"{Fore.RED}ID or Name must be specified. Use --help for more information.{Style.RESET_ALL}")
            return None

        challenge: ChallengeInfo = self.client.get_challenge(challenge_id_or_name=self.challenge_id if self.challenge_id else self.challenge_name)
        if not challenge.docker:
            self.logger.error(f'{Fore.RED}Challenge "{challenge.name}" does not provide an instance.{Style.RESET_ALL}')
            return None

        if self.instance_command == "start":
            self.start_instance(challenge=challenge)
        elif self.instance_command == "stop":
            self.stop_instance(challenge=challenge)
        elif self.instance_command == "status":
            self.status_instance(challenge=challenge)


    def download_writeup(self):
        if self.challenge_id is None and self.challenge_name is None:
            self.logger.error(f"{Fore.RED}ID or Name must be specified. Use --help for more information.{Style.RESET_ALL}")
            return None

        challenge: ChallengeInfo = self.client.get_challenge(challenge_id_or_name=self.challenge_id if self.challenge_id else self.challenge_name)
        if challenge is None:
            self.logger.error(f'{Fore.RED}Challenge not found.{Style.RESET_ALL}')
            return None

        if not challenge.writeup_provided:
            self.logger.error(f'{Fore.RED}Writeup is not provided.{Style.RESET_ALL}')
            return None

        self.logger.info(f'{Fore.GREEN}Writeup is downloading...{Style.RESET_ALL}')
        target_path = challenge.download_writeup(path=self.args.path)
        if target_path is None:
            return None

        self.logger.info(f'{Fore.GREEN}Integrity check successful{Style.RESET_ALL}')
        self.logger.info(f'{Fore.GREEN}Writeup downloaded in {target_path}{Style.RESET_ALL}')

    def search(self):
        if self.args.unsolved:
            unsolved = self.args.unsolved
        elif self.args.solved:
            unsolved = not self.args.solved
        else:
            unsolved = None

        # Mapping between category-id and category_name. Challenge returns only the id.
        categories: List[Category] = self.client.get_challenge_categories_list()
        category_dict = {x.id: x.name for x in categories}

        cat_filter_list = self._get_filter_category_list(category_dict)

        challenges_list: List[ChallengeList] = self.client.search_challenges(name=self.challenge_name,
                                                                             unsolved=unsolved,
                                                                             filter_todo=self.args.todo,
                                                                             filter_category_list=cat_filter_list,
                                                                             filter_difficulty=self.args.difficulty)
        if len(challenges_list) == 0:
            self.logger.warning(
                f'{Fore.LIGHTYELLOW_EX}No challenges found for name "{self.challenge_name}"{Style.RESET_ALL}')
            return None

        categories = self.client.get_challenge_categories_list()
        category_dict = {x.id: x.name for x in categories}

        self.console.print((create_table_challenge_list(challenge_list=sorted([x.to_dict() for x in challenges_list], key=lambda x: x["difficulty_num"]),
                                                        category_dict=category_dict)))
        self.logger.info(f'{Fore.GREEN}Found {len(challenges_list)} challenges which begin with "{self.challenge_name}"{Style.RESET_ALL}')


    def execute(self):
        """Download the challenge."""
        if not self.challenge_command:
            self.logger.error(f"{Fore.RED}No options. Use --help for more information.{Style.RESET_ALL}")
            return None
        elif self.challenge_command == "submit":
            self.submit()
        elif self.challenge_command == "download":
            self.download()
        elif self.challenge_command == "info":
            self.print_info()
        elif self.challenge_command == "list":
            self.list_challenges()
        elif self.challenge_command == "instance":
            self.handle_instance()
        elif self.challenge_command == "download_writeup":
            self.download_writeup()
        elif self.challenge_command == "search":
            self.search()
