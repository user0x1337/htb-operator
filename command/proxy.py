import argparse

from command.base import BaseCommand


class ProxyCommand(BaseCommand):

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)

    def execute(self):
        if self.args.clear:
            if "Proxy" not in self.htb_cli.config:
                return None

            self.htb_cli.config["Proxy"].clear()
            del self.htb_cli.config["Proxy"]
            self.htb_cli.save_config_file()
        elif self.args.http:
            proxy_list = self.args.http.strip().split(",")
            if "Proxy" not in self.htb_cli.config:
                self.htb_cli.config["Proxy"] = {"http": proxy_list[0]}
            else:
                self.htb_cli.config["Proxy"]["http"] = proxy_list[0]

            if len(proxy_list) > 1:
                self.htb_cli.config["Proxy"]["https"] = proxy_list[1]

            self.htb_cli.config["Proxy"]["verify_ssl"] = str(False)
            self.htb_cli.save_config_file()
        else:
            pass