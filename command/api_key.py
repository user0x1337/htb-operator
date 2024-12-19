import argparse
from datetime import datetime, timezone
from typing import Optional

import jwt

from command.base import BaseCommand


class ApiKey(BaseCommand):
    api_key: Optional[str]

    # noinspection PyUnresolvedReferences
    def __init__(self, htb_cli: "HtbCLI", args: argparse.Namespace):
        super().__init__(htb_cli=htb_cli, args=args)
        self.api_key = htb_cli.api_key

    def check_api_key(self, api_key) -> bool:
        """Decodes the JWT and extracts important information."""
        try:
            current_time = datetime.now(tz=timezone.utc)
            # Assuming the JWT is not signed (no secret or algorithm validation here for simplicity)
            decoded = jwt.decode(api_key, options={"verify_signature": False})
            expire = decoded.get('exp', 'Unknown')
            # Convert exp to readable date if it's a valid timestamp
            if isinstance(expire, (int, float)):
                exp_date = datetime.fromtimestamp(expire, tz=timezone.utc)
            else:
                self.logger.error('Invalid expiration date')
                return False

            self.logger.info(f"API Key expires: {exp_date.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            if current_time > exp_date:
                self.logger.error(f"API Key is expired and thus invalid. Please create a new one.")
                return False
            else:
                self.logger.info(f"API Key is valid.")

                return True
        except jwt.DecodeError:
            self.logger.error(f"Invalid JWT token.")
            return False


    def execute(self):
        if self.args.check:
            self.check_api_key(self.api_key)
        elif self.args.renew:
            new_api_key = self.args.renew
            # Check API-Key
            if self.check_api_key(new_api_key):
                self.htb_cli.config["HTB"]["api_key"] = new_api_key
                self.htb_cli.save_config_file()
                self.logger.info("New API key successfully renewed.")
            else:
                return None
