from __future__ import annotations

from typing import Any

from etl.models.metadata import InstrumentDefinition


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
    row = {
        field: coerce_value(record.get(field))
        for field in allowed_fields
    }
    row["_synced_at"] = synced_at
    row["_etl_run_id"] = etl_run_id
    row["_source_mode"] = source_mode
    return row
