from __future__ import annotations

from etl.config import Settings
from etl.extract.base import RedcapClientProtocol
from etl.extract.mock_client import MockRedcapClient
from etl.extract.production_client import ProductionRedcapClient


def get_redcap_client(settings: Settings) -> RedcapClientProtocol:
    if settings.redcap_mock_enabled:
        return MockRedcapClient(settings)
    return ProductionRedcapClient(settings)
