from __future__ import annotations

from typing import Any

import requests
import structlog

from etl.config import Settings
from etl.extract.metadata_normalizer import normalize_metadata
from etl.models.metadata import MetadataModel

logger = structlog.get_logger(__name__)

# The hosted mock REDCap service (https://mock-redcap-service.onrender.com)
# uses /api/* paths without a /redcap/ sub-prefix. All paths below match the
# actual Render deployment. When real REDCap is available, swap to the
# ProductionRedcapClient instead.


class MockRedcapClient:
    """HTTP adapter for the NEPS mock REDCap API hosted on Render.

    Base URL example: https://mock-redcap-service.onrender.com
    All endpoints are at /api/<resource>.
    """

    source_mode = "mock"

    def __init__(self, settings: Settings) -> None:
        # Strip trailing slash; endpoints will be appended as /api/<resource>
        self._base_url = settings.redcap_api_url.rstrip("/")
        self._timeout = settings.http_timeout_seconds
        self._session = requests.Session()
        # Render free-tier may be asleep — allow a generous timeout
        self._session.headers.update({"Accept": "application/json"})

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self._base_url}{path}"
        response = self._session.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict[str, Any]:
        return self._get("/health")

    def export_metadata(self) -> MetadataModel:
        """
        The Render mock does not expose /export/metadata.
        We call /api/stats to wake the service and build metadata
        from the known instrument schema.
        """
        # Wake the service and confirm it is up
        self._get("/api/stats")

        # Construct a synthetic metadata payload that matches the mock schema
        raw = {
            "project_id": "NEPS-2025",
            "project_title": "NEPS Digital - Youth Mental Health Observatory",
            "events": [
                {"event_name": "baseline_arm_1", "arm_num": 1, "day_offset": 0},
                {"event_name": "month_1_arm_1", "arm_num": 1, "day_offset": 30},
                {"event_name": "month_6_arm_1", "arm_num": 1, "day_offset": 180},
                {"event_name": "month_12_arm_1", "arm_num": 1, "day_offset": 365},
                {"event_name": "month_18_arm_1", "arm_num": 1, "day_offset": 545},
                {"event_name": "month_24_arm_1", "arm_num": 1, "day_offset": 730},
            ],
            "instruments": [
                {"instrument_name": "demographics", "instrument_label": "Demographics"},
                {"instrument_name": "monthly_self_report", "instrument_label": "Monthly Self-Report"},
                {"instrument_name": "comprehensive_wave", "instrument_label": "Comprehensive Survey Wave"},
                {"instrument_name": "distress_screening", "instrument_label": "Distress Screening"},
                {"instrument_name": "wp6_session", "instrument_label": "WP6 Session Record"},
            ],
        }
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

        # ── 1. Demographics ──────────────────────────────────────────────
        participants_payload = self._get("/api/participants", params={"limit": 500})
        participants = participants_payload.get("data", [])
        demographics = [
            {
                **p,
                "record_id": p.get("participant_id") or p.get("record_id"),
                "redcap_event_name": p.get("redcap_event_name", "baseline_arm_1"),
                "redcap_data_access_group": p.get("site", "").lower().replace(" ", "_") if p.get("site") else "",
                "redcap_repeat_instrument": "",
                "redcap_repeat_instance": "",
                "_instrument": "demographics",
            }
            for p in participants
        ]

        # ── 2. Monthly self-reports + comprehensive waves ─────────────────
        monthly_payload = self._get("/api/export/records", params={"format": "json"})
        instrument_records: list[dict[str, Any]] = []
        if isinstance(monthly_payload, list):
            for record in monthly_payload:
                instrument = record.get("redcap_repeat_instrument") or "monthly_self_report"
                instrument_records.append({**record, "_instrument": instrument})

        # ── 3. Distress screenings ────────────────────────────────────────
        distress_payload = self._get("/api/distress-screenings")
        distress_records = [
            {
                **s,
                "record_id": s.get("participant_id") or s.get("record_id"),
                "redcap_event_name": s.get("redcap_event_name", "baseline_arm_1"),
                "redcap_repeat_instrument": "",
                "redcap_repeat_instance": "",
                "_instrument": "distress_screening",
            }
            for s in distress_payload.get("screenings", [])
        ]

        # ── 4. WP6 sessions ───────────────────────────────────────────────
        wp6_records: list[dict[str, Any]] = []
        for participant in participants:
            record_id = participant.get("participant_id") or participant.get("record_id", "")
            if not record_id:
                continue
            try:
                wp6_payload = self._get(f"/api/wp6-sessions/{record_id}")
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    continue
                raise

            for session in wp6_payload.get("sessions", []):
                wp6_records.append(
                    {
                        **session,
                        "record_id": session.get("participant_id") or session.get("record_id"),
                        "redcap_event_name": session.get("redcap_event_name", "baseline_arm_1"),
                        "redcap_repeat_instrument": "wp6_session",
                        "redcap_repeat_instance": str(session.get("session_number", "")),
                        "_instrument": "wp6_session",
                    }
                )

        return demographics + instrument_records + distress_records + wp6_records
