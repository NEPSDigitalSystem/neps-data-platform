from __future__ import annotations

from typing import Any

import requests
import structlog

from etl.config import Settings
from etl.extract.metadata_normalizer import normalize_metadata
from etl.models.metadata import MetadataModel

logger = structlog.get_logger(__name__)


class MockRedcapClient:
    """HTTP adapter for mock REDCap API served by neps-backend."""

    source_mode = "mock"

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.redcap_api_url.rstrip("/")
        self._timeout = settings.http_timeout_seconds
        self._session = requests.Session()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self._base_url}{path}"
        response = self._session.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict[str, Any]:
        return self._get("/health")

    def export_metadata(self) -> MetadataModel:
        raw = self._get("/export/metadata")
        return normalize_metadata(raw, source_mode="mock")

    def export_records(
        self,
        *,
        fields: list[str] | None = None,
        events: list[str] | None = None,
        date_range_begin: str | None = None,
    ) -> list[dict[str, Any]]:
        if date_range_begin:
            logger.warning(
                "mock_incremental_not_supported",
                date_range_begin=date_range_begin,
            )

        params: dict[str, Any] = {"format": "json"}
        if fields:
            params["fields"] = fields
        if events:
            params["events"] = events

        survey_records = self._get("/export/records", params=params)
        if not isinstance(survey_records, list):
            survey_records = []

        participants_payload = self._get("/participants", params={"limit": 500})
        participants = participants_payload.get("data", [])
        demographics = [
            {
                **participant,
                "redcap_repeat_instrument": "",
                "redcap_repeat_instance": "",
                "_instrument": "demographics",
            }
            for participant in participants
        ]

        distress_payload = self._get("/screenings/distress")
        distress_records = [
            {
                **screening,
                "redcap_repeat_instrument": "",
                "redcap_repeat_instance": "",
                "_instrument": "distress_screening",
            }
            for screening in distress_payload.get("screenings", [])
        ]

        wp6_records: list[dict[str, Any]] = []
        for participant in participants:
            record_id = participant["record_id"]
            try:
                wp6_payload = self._get(f"/wp6/sessions/{record_id}")
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    continue
                raise

            for session in wp6_payload.get("sessions", []):
                wp6_records.append(
                    {
                        **session,
                        "redcap_repeat_instrument": "wp6_session",
                        "redcap_repeat_instance": str(session.get("session_number", "")),
                        "_instrument": "wp6_session",
                    }
                )

        instrument_records: list[dict[str, Any]] = []
        for record in survey_records:
            instrument = record.get("redcap_repeat_instrument") or "monthly_self_report"
            instrument_records.append({**record, "_instrument": instrument})

        return demographics + instrument_records + distress_records + wp6_records
