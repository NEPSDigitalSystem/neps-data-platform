from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Engine


class SyncStateStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get_watermark(self, *, project_id: str, entity_name: str) -> str | None:
        with self._engine.connect() as connection:
            result = connection.execute(
                text(
                    """
                    SELECT last_modified_at
                    FROM redcap.etl_sync_state
                    WHERE project_id = :project_id AND entity_name = :entity_name
                    """
                ),
                {"project_id": project_id, "entity_name": entity_name},
            ).scalar_one_or_none()
        return result.isoformat() if isinstance(result, datetime) else result

    def update_state(
        self,
        *,
        project_id: str,
        entity_name: str,
        metadata_hash: str,
        source_mode: str,
        last_modified_at: datetime | None = None,
    ) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO redcap.etl_sync_state (
                        project_id, entity_name, metadata_hash, source_mode,
                        last_modified_at, last_run_at
                    ) VALUES (
                        :project_id, :entity_name, :metadata_hash, :source_mode,
                        :last_modified_at, :last_run_at
                    )
                    ON CONFLICT (project_id, entity_name)
                    DO UPDATE SET
                        metadata_hash = EXCLUDED.metadata_hash,
                        source_mode = EXCLUDED.source_mode,
                        last_modified_at = EXCLUDED.last_modified_at,
                        last_run_at = EXCLUDED.last_run_at
                    """
                ),
                {
                    "project_id": project_id,
                    "entity_name": entity_name,
                    "metadata_hash": metadata_hash,
                    "source_mode": source_mode,
                    "last_modified_at": last_modified_at,
                    "last_run_at": datetime.now(timezone.utc),
                },
            )
