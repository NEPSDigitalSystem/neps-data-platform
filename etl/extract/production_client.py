from __future__ import annotations

import time
from typing import Any

import requests
import structlog

from etl.config import Settings
from etl.extract.metadata_normalizer import normalize_metadata
from etl.models.metadata import MetadataModel

logger = structlog.get_logger(__name__)


class ProductionRedcapClient:
    """Native REDCap REST API client (POST /api/)."""

    source_mode = "production"

    def __init__(self, settings: Settings) -> None:
        self._api_url = settings.redcap_api_url.rstrip("/")
        self._token = settings.redcap_api_token or ""
        self._timeout = settings.http_timeout_seconds
        self._max_retries = settings.http_max_retries
        self._session = requests.Session()

    def _post(self, payload: dict[str, Any]) -> Any:
        data = {"token": self._token, **payload}
        last_error: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                response = self._session.post(
                    self._api_url,
                    data=data,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                if payload.get("format") == "json":
                    return response.json()
                return response.text
            except requests.RequestException as exc:
                last_error = exc
                logger.warning("redcap_request_failed", attempt=attempt, error=str(exc))
                if attempt < self._max_retries:
                    time.sleep(2 ** attempt)

        assert last_error is not None
        raise last_error

    def health_check(self) -> dict[str, Any]:
        metadata = self._post({"content": "exportMetadata", "format": "json"})
        return {
            "status": "connected",
            "mode": "production",
            "field_count": len(metadata) if isinstance(metadata, list) else 0,
        }

    def export_metadata(self) -> MetadataModel:
        raw = self._post({"content": "exportMetadata", "format": "json"})
        if not isinstance(raw, list):
            raise ValueError("Unexpected REDCap metadata response")
        return normalize_metadata(raw, source_mode="production")

    def export_records(
        self,
        *,
        fields: list[str] | None = None,
        events: list[str] | None = None,
        date_range_begin: str | None = None,
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "content": "exportRecords",
            "format": "json",
            "type": "flat",
            "rawOrLabel": "raw",
        }
        if fields:
            payload["fields"] = fields
        if events:
            payload["events"] = events
        if date_range_begin:
            payload["dateRangeBegin"] = date_range_begin

        records = self._post(payload)
        if not isinstance(records, list):
            raise ValueError("Unexpected REDCap records response")

        for record in records:
            instrument = record.get("redcap_repeat_instrument") or "demographics"
            record["_instrument"] = instrument

        return records
