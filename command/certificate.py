import argparse
from typing import Optional

from colorama import Fore, Style
from rich.table import Table

from command.base import BaseCommand
from console.cli_panel import format_bool
from htbapi import RequestException, Certificate


class CertificateCommand(BaseCommand):
    certificate_command: Optional[str]
    id: Optional[int]
    list: Optional[str]
    filename: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        self.certificate_command = args.certificate if hasattr(args, "certificate") else None
        self.id = args.id if hasattr(args, "id") else None
        self.list = args.list if hasattr(args, "list") else None
        self.filename = args.filename if hasattr(args, "filename") else None


    def execute(self):
        """Certificate command"""
        if not self.list and not self.certificate_command:
            self.logger.error("No options. Use --help for more information.")
        elif self.list:
            certs:[Certificate] = self.client.get_prolab_certificate_list()
            if len(certs) == 0:
                self.logger.warning("No certificates obtained, yet.")
                return None

            table = Table(title="Obtained Certifications", show_lines=True)
            table.add_column(header="Certification ID", style="cyan", justify="left")
            table.add_column(header="Name", style="cyan", justify="left")
            table.add_column(header="Downloaded", style="cyan", justify="left")
            table.add_column(header="Completion date/time", style="cyan", justify="left")

            for cert in certs:
                table.add_row(str(cert.cert_id), cert.name, format_bool(cert.has_downloaded_cert), f"{cert.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")

            self.console.print(table)

        elif self.certificate_command and self.id:
            try:
                path = self.client.download_prolab_certificate(self.id, path=self.filename)
                self.logger.info(f"{Fore.GREEN}Certificate successfully downloaded in {path}{Style.RESET_ALL}")
            except RequestException as e:
                self.logger.error(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                return None