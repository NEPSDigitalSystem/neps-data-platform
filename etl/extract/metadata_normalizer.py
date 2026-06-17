from __future__ import annotations

from typing import Any

from etl.models.metadata import MetadataModel
from etl.transform.mock_schema import get_backend_instruments


def normalize_metadata(raw: Any, *, source_mode: str) -> MetadataModel:
    if source_mode == "mock":
        if not isinstance(raw, dict):
            raise ValueError("Mock metadata must be a JSON object")
        return MetadataModel(
            project_id=str(raw.get("project_id", "NEPS-2025")),
            project_title=str(raw.get("project_title", "NEPS Digital")),
            instruments=get_backend_instruments(),
            events=list(raw.get("events", [])),
            raw=raw,
            source_mode="mock",
        )

    if not isinstance(raw, list):
        raise ValueError("Production metadata must be a list of field definitions")

    return MetadataModel(
        project_id="production",
        project_title="REDCap Production Project",
        instruments=get_backend_instruments(),
        events=[],
        raw={"fields": raw},
        source_mode="production",
    )
