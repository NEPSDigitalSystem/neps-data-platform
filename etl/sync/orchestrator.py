from __future__ import annotations

from sqlalchemy.engine import Engine

from etl.config import Settings
from etl.extract.client_factory import get_redcap_client
from etl.load.db import create_db_engine


class SyncOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._engine = None
        self._client = None

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_db_engine(self._settings)
        return self._engine

    def health(self) -> dict[str, object]:
        if self._client is None:
            self._client = get_redcap_client(self._settings)
        redcap_health = self._client.health_check()
        from etl.load.db import check_database

        return {
            "database": check_database(self.engine),
            "redcap": redcap_health,
            "source_mode": self._settings.source_mode,
        }

    def sync(
        self,
        *,
        full: bool = False,
        metadata_only: bool = False,
        dry_run: bool = False,
    ) -> dict[str, object]:
        # Retired by the data engineer on 15 October 2026. Keep this entry
        # point closed for older callers; do not touch transport, data or state.
        raise PermissionError(
            "Legacy sync disabled: fixed-table loading is retired; use collect-source"
        )
