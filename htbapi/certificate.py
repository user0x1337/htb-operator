from datetime import datetime
from typing import Optional
from htbapi import client
import dateutil.parser


class Certificate(client.BaseHtbApiObject):
    """Certificate object."""
    name: str
    cover_img_url: Optional[str]
    has_downloaded_cert: bool
    cert_id: int
    created_at: datetime

    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "HTBClient"):
        self._client = _client
        self.name = data['prolabName']
        self.cover_img_url = data.get('cover_img_url', None)
        self.has_downloaded_cert = data.get('hasDownloadedCert', False)
        self.cert_id = data.get('certId', -1)
        self.created_at = dateutil.parser.parse(data.get('created_at'))

    def __repr__(self):
        return f"<Certificate '{self.name} | {self.id}'>"

    def to_dict(self):
        return {
            "Name": self.name,
            "cover_img_url": self.cover_img_url,
            "has_downloaded_cert": self.has_downloaded_cert,
            "cert_id": self.cert_id,
            "created_at": self.created_at
        }