from __future__ import annotations

import re
from typing import Any


def route_record_to_instrument(record: dict[str, Any]) -> str:
    if explicit := record.get("_instrument"):
        return str(explicit)

    repeat_instrument = record.get("redcap_repeat_instrument")
    if repeat_instrument:
        return str(repeat_instrument)

    if "screening_date" in record and "distress_score" in record:
        return "distress_screening"

    if "session_number" in record and "attendance" in record:
        return "wp6_session"

    if "country" in record and "cohort_status" in record:
        return "demographics"

    return "monthly_self_report"


def normalize_record(record: dict[str, Any], *, source_mode: str) -> dict[str, Any]:
    normalized = {k: ("" if v is None else v) for k, v in record.items() if not k.startswith("_")}
    normalized.setdefault("redcap_repeat_instrument", "")
    normalized.setdefault("redcap_repeat_instance", "")
    normalized["_source_mode"] = source_mode
    return normalized


def group_records_by_instrument(
    records: list[dict[str, Any]],
    *,
    source_mode: str,
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        instrument = route_record_to_instrument(record)
        grouped.setdefault(instrument, []).append(
            normalize_record(record, source_mode=source_mode)
        )
    return grouped
