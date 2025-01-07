import argparse
import getpass
from typing import Optional
from urllib.parse import unquote

import requests
from colorama import Fore, Style
from requests import Session, codes
from urllib3.exceptions import InsecureRequestWarning

from command.base import BaseCommand


class InitCommand(BaseCommand):

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _new_session(self, cookies) -> Session:
        sess: Session = requests.session()
        sess.proxies = self.academy_client.academy_http_request._proxies
        sess.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"}

        return sess

    def execute(self) -> Optional[dict]:
        # TODO: Refactor and move the code to academy_http_request/academy_client with an own method
        user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
        sess: Session = requests.session()
        sess.proxies = self.academy_client.academy_http_request._proxies
        sess.headers = {"User-Agent": user_agent}
        sess.verify = False

        r = sess.get(url="https://academy.hackthebox.com/login",
                     headers={"Referer": "https://academy.hackthebox.com/",
                              "User-Agent": user_agent})

        if r.status_code != codes.found:
            r = sess.get(url="https://academy.hackthebox.com/sso/redirect")
            if r.status_code != codes.ok:
                self.logger.error(f"{Fore.RED}Error during login process: {r.text} (Status code: {r.status_code}){Style.RESET_ALL}")
                return None

            username = input("Username: ")
            password = getpass.getpass("Password: ")
            r = sess.post(url="https://account.hackthebox.com/api/v1/auth/login",
                          json={"email": username, "password": password, "remember": True},
                          headers={"X-Requested-With": "XMLHttpRequest",
                                   "User-Agent": user_agent,
                                   "Accept": "application/json",
                                   "Accept-Encoding": "gzip, deflate, br",
                                   "X-Xsrf-Token": unquote(r.cookies["XSRF-TOKEN"])})

            if r.status_code != codes.ok:
                self.logger.error(f"{Fore.RED}Login failed: {r.json()["message"]}{Style.RESET_ALL}")
                return None

            two_factor_needed: bool = r.json()["two_factor"]
            if two_factor_needed:
                two_factor = input("OTP token: ")
                r = sess.post(url="https://account.hackthebox.com/api/v1/auth/two-factor-challenge",
                              json={"code": two_factor},
                              cookies=r.cookies,
                              headers={"X-Requested-With": "XMLHttpRequest",
                                       "User-Agent": user_agent,
                                       "Accept": "application/json",
                                       "Accept-Encoding": "gzip, deflate, br",
                                       "X-Xsrf-Token": unquote(r.cookies["XSRF-TOKEN"])}
                              )
                if r.status_code != codes.ok:
                    self.logger.error(f"{Fore.RED}Login failed: {r.json()["message"]}{Style.RESET_ALL}")
                    return None


            intended_route = unquote(r.json()["intended_route"])
            r = sess.get(url=intended_route,
                         cookies=r.cookies,
                         headers={"Referer": "https://account.hackthebox.com/login", "User-Agent": user_agent})

            cookies_dict = r.cookies.get_dict()
            res_cookies = {}
            for k, v in cookies_dict.items():
                if "remember" in k:
                    res_cookies[k] = v
                elif "htb_academy_session" in k:
                    res_cookies[k] = v
                elif "htb_academy_session" in k:
                    res_cookies[k] = v

            self.logger.info(f"{Fore.GREEN}Login successful{Style.RESET_ALL}")
            self.logger.info(f"{Fore.GREEN}Session tokens saved. Init completed. Having fun with academy commands.{Style.RESET_ALL}")

            return res_cookies
        else:
            self.logger.info(f"{Fore.GREEN}Init still valid. Conducting login procedure is not necessary.{Style.RESET_ALL}")
            return None