from __future__ import annotations

from typing import Any

from etl.models.metadata import InstrumentDefinition


<<<<<<< Updated upstream
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
=======
def record_conflict_keys(instrument: InstrumentDefinition) -> list[str]:
    if instrument.repeating:
        return [
            "record_id",
            "redcap_event_name",
            "redcap_repeat_instrument",
            "redcap_repeat_instance",
        ]
    if instrument.instrument_name == "distress_screening":
        return ["record_id", "screening_date"]
    return ["record_id", "redcap_event_name"]
>>>>>>> Stashed changes


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
<<<<<<< Updated upstream
    return {
        field: coerce_value(record.get(field))
        for field in allowed_fields
        if field in record
    }
=======
    row = {
        field: coerce_value(record.get(field))
        for field in allowed_fields
    }
    row["_synced_at"] = synced_at
    row["_etl_run_id"] = etl_run_id
    row["_source_mode"] = source_mode
    return row
>>>>>>> Stashed changes
