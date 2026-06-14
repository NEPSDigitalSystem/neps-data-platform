from __future__ import annotations

from typing import Any, Protocol

from etl.models.metadata import MetadataModel


class RedcapClientProtocol(Protocol):
    source_mode: str

    def health_check(self) -> dict[str, Any]: ...

    def export_metadata(self) -> MetadataModel: ...

    def export_records(
        self,
        *,
        fields: list[str] | None = None,
        events: list[str] | None = None,
        date_range_begin: str | None = None,
    ) -> list[dict[str, Any]]: ...
