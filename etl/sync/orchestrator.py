from __future__ import annotations

from datetime import datetime, timezone

import structlog
from sqlalchemy.engine import Engine

from etl.config import Settings
from etl.extract.client_factory import get_redcap_client
from etl.load.db import create_db_engine
from etl.load.upsert import load_instrument_records, persist_metadata, refresh_views
from etl.sync.run_log import RunLogger
from etl.sync.state import SyncStateStore
from etl.transform.normalizer import group_records_by_instrument

logger = structlog.get_logger(__name__)


class SyncOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._engine = create_db_engine(settings)
        self._client = get_redcap_client(settings)
        self._state = SyncStateStore(self._engine)

    @property
    def engine(self) -> Engine:
        return self._engine

    def health(self) -> dict[str, object]:
        redcap_health = self._client.health_check()
        from etl.load.db import check_database

        return {
            "database": check_database(self._engine),
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
        run_logger = RunLogger(self._engine)
        sync_type = "full" if full else "incremental"
        project_id = self._settings.redcap_project_id

        run_logger.start(
            source_mode=self._settings.source_mode,
            project_id=project_id,
            sync_type=sync_type,
        )

        try:
            metadata = self._client.export_metadata()
            logger.info("metadata_exported", instrument_count=len(metadata.instruments))

            if dry_run:
                run_logger.finish(status="success", records_extracted=0, records_loaded=0)
                return {
                    "status": "dry_run",
                    "metadata_hash": metadata.metadata_hash(),
                    "instruments": [i.instrument_name for i in metadata.instruments],
                }

            if not metadata_only:
                watermark = None if full else self._state.get_watermark(
                    project_id=project_id,
                    entity_name="records",
                )
                records = self._client.export_records(date_range_begin=watermark)
                grouped = group_records_by_instrument(
                    records,
                    source_mode=self._settings.source_mode,
                )
            else:
                records = []
                grouped = {}

            loaded_total = 0
            synced_at = datetime.now(timezone.utc).isoformat()

            with self._engine.begin() as connection:
                persist_metadata(connection, metadata, project_id=project_id)

            if not metadata_only:
                for instrument in metadata.instruments:
                    instrument_records = grouped.get(instrument.instrument_name, [])
                    loaded = load_instrument_records(
                        self._engine,
                        instrument,
                        instrument_records,
                        synced_at=synced_at,
                        etl_run_id=run_logger.run_id,
                        source_mode=self._settings.source_mode,
                    )
                    loaded_total += loaded
                    logger.info(
                        "instrument_loaded",
                        instrument=instrument.instrument_name,
                        rows=loaded,
                    )

                refresh_views(self._engine, metadata)

            self._state.update_state(
                project_id=project_id,
                entity_name="records",
                metadata_hash=metadata.metadata_hash(),
                source_mode=self._settings.source_mode,
                last_modified_at=datetime.now(timezone.utc),
            )

            run_logger.finish(
                status="success",
                records_extracted=len(records),
                records_loaded=loaded_total,
            )

            return {
                "status": "success",
                "run_id": run_logger.run_id,
                "records_extracted": len(records),
                "records_loaded": loaded_total,
                "sync_type": sync_type,
                "source_mode": self._settings.source_mode,
            }
        except Exception as exc:
            logger.exception("sync_failed", error=str(exc))
            run_logger.finish(status="failed", error_message=str(exc))
            raise
