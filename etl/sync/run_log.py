from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Engine


class RunLogger:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self.run_id = str(uuid.uuid4())

    def start(self, *, source_mode: str, project_id: str, sync_type: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO redcap.etl_run_log (
                        run_id, started_at, status, source_mode, project_id, sync_type
                    ) VALUES (
                        :run_id, :started_at, 'running', :source_mode, :project_id, :sync_type
                    )
                    """
                ),
                {
                    "run_id": self.run_id,
                    "started_at": datetime.now(timezone.utc),
                    "source_mode": source_mode,
                    "project_id": project_id,
                    "sync_type": sync_type,
                },
            )

    def finish(
        self,
        *,
        status: str,
        records_extracted: int = 0,
        records_loaded: int = 0,
        error_message: str | None = None,
    ) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE redcap.etl_run_log
                    SET finished_at = :finished_at,
                        status = :status,
                        records_extracted = :records_extracted,
                        records_loaded = :records_loaded,
                        error_message = :error_message
                    WHERE run_id = :run_id
                    """
                ),
                {
                    "run_id": self.run_id,
                    "finished_at": datetime.now(timezone.utc),
                    "status": status,
                    "records_extracted": records_extracted,
                    "records_loaded": records_loaded,
                    "error_message": error_message,
                },
            )
