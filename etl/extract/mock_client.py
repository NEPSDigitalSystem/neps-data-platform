from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any, Iterable

import requests
import structlog

from etl.config import Settings
from etl.extract.metadata_normalizer import normalize_metadata
from etl.models.metadata import MetadataModel

logger = structlog.get_logger(__name__)


class MockRedcapClient:
    """HTTP adapter for mock REDCap API served by neps-backend or Render."""

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
        params: dict[str, Any] = {"format": "json"}
        if fields:
            params["fields"] = fields
        if events:
            params["events"] = events
        if date_range_begin:
            params["date_range_begin"] = date_range_begin
            params["dateRangeBegin"] = date_range_begin

        survey_payload = self._get("/export/records", params=params)
        survey_records = survey_payload if isinstance(survey_payload, list) else []
        survey_records = _filter_since(
            survey_records,
            date_range_begin,
            ("updated_at", "created_at", "survey_date"),
        )

        participant_params = _with_watermark({"limit": 500}, date_range_begin)
        participants_payload = self._get("/participants", params=participant_params)
        participants = participants_payload.get("data", [])
        participant_records = [
            {**participant, "_entity": "participants", "_instrument": "demographics"}
            for participant in _filter_since(
                participants,
                date_range_begin,
                ("updated_at", "created_at", "enrollment_date"),
            )
        ]

        consent_records: list[dict[str, Any]] = []
        for participant in participants:
            record_id = participant["record_id"]
            try:
                consent = self._get(f"/participants/{record_id}/consent")
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    continue
                raise
            if not isinstance(consent, dict) or "error" in consent:
                continue
            if _is_since(consent, date_range_begin, ("updated_at", "created_at", "re_consent_date", "consent_date")):
                consent_records.append({**consent, "_entity": "consent_records"})

        distress_payload = self._get(
            "/screenings/distress",
            params=_with_watermark({}, date_range_begin),
        )
        distress_records = [
            {**screening, "_entity": "distress_screenings"}
            for screening in _filter_since(
                distress_payload.get("screenings", []),
                date_range_begin,
                ("updated_at", "created_at", "screening_date"),
            )
        ]

        referral_records: list[dict[str, Any]] = []
        try:
            referrals_payload = self._get("/referrals", params=_with_watermark({}, date_range_begin))
        except requests.HTTPError as exc:
            if exc.response is None or exc.response.status_code != 404:
                raise
        else:
            referrals = referrals_payload.get("referrals", referrals_payload.get("data", []))
            referral_records = [
                {**referral, "_entity": "referrals"}
                for referral in _filter_since(
                    referrals,
                    date_range_begin,
                    ("updated_at", "created_at", "initiation_date", "follow_up_date"),
                )
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

            for session in _filter_since(
                wp6_payload.get("sessions", []),
                date_range_begin,
                ("updated_at", "created_at", "session_date"),
            ):
                wp6_records.append({**session, "_entity": "wp6_sessions"})

        instrument_records: list[dict[str, Any]] = []
        for record in survey_records:
            instrument = record.get("redcap_repeat_instrument") or "monthly_self_report"
            instrument_records.append(
                {**record, "_entity": "survey_responses", "_instrument": instrument}
            )

        return (
            participant_records
            + consent_records
            + instrument_records
            + distress_records
            + referral_records
            + wp6_records
        )


def _with_watermark(params: dict[str, Any], date_range_begin: str | None) -> dict[str, Any]:
    if not date_range_begin:
        return params
    return {
        **params,
        "date_range_begin": date_range_begin,
        "dateRangeBegin": date_range_begin,
    }


def _filter_since(
    records: Iterable[dict[str, Any]],
    date_range_begin: str | None,
    date_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if _is_since(record, date_range_begin, date_fields)
    ]


def _is_since(
    record: dict[str, Any],
    date_range_begin: str | None,
    date_fields: tuple[str, ...],
) -> bool:
    watermark = _parse_datetime(date_range_begin)
    if watermark is None:
        return True

    record_time = _record_datetime(record, date_fields)
    if record_time is None:
        return False

    return record_time >= watermark


def _record_datetime(record: dict[str, Any], date_fields: tuple[str, ...]) -> datetime | None:
    parsed = [
        value
        for field in date_fields
        if (value := _parse_datetime(record.get(field))) is not None
    ]
    if not parsed:
        return None
    return max(parsed)


def _parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None

    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, time.min)
    elif isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            try:
                parsed = datetime.combine(date.fromisoformat(value[:10]), time.min)
            except ValueError:
                return None
    else:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
