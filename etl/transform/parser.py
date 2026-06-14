from __future__ import annotations

from typing import Any

from etl.models.metadata import InstrumentDefinition


CONFLICT_KEYS: dict[str, list[str]] = {
    "participants": ["record_id"],
    "consent_records": ["record_id"],
    "survey_responses": ["record_id", "month"],
    "distress_screenings": ["record_id", "screening_date"],
    "referrals": ["referral_id"],
    "wp6_sessions": ["record_id", "session_number"],
}


def record_conflict_keys(instrument: InstrumentDefinition) -> list[str]:
    return CONFLICT_KEYS.get(instrument.instrument_name, ["record_id"])


def coerce_value(value: Any) -> Any:
    if value is None or value == "":
        return None
    return value


def prepare_row(
    record: dict[str, Any],
    instrument: InstrumentDefinition,
    *,
    synced_at: str,
    etl_run_id: str,
    source_mode: str,
) -> dict[str, Any]:
    allowed_fields = {field.field_name for field in instrument.fields}
    return {
        field: coerce_value(record.get(field))
        for field in allowed_fields
        if field in record
    }
