from __future__ import annotations

import re
from typing import Any


REDCAP_INSTRUMENT_TO_ENTITY = {
    "demographics": "participants",
    "monthly_self_report": "survey_responses",
    "comprehensive_wave": "survey_responses",
    "distress_screening": "distress_screenings",
    "wp6_session": "wp6_sessions",
    "consent_record": "consent_records",
    "consent_records": "consent_records",
    "referral": "referrals",
    "referrals": "referrals",
}


def _entity_name(name: Any) -> str | None:
    if not name:
        return None
    return REDCAP_INSTRUMENT_TO_ENTITY.get(str(name), str(name))


def route_record_to_instrument(record: dict[str, Any]) -> str:
    if explicit := _entity_name(record.get("_entity")):
        return explicit
    if explicit := _entity_name(record.get("_instrument")):
        return explicit
    if repeat_instrument := _entity_name(record.get("redcap_repeat_instrument")):
        return repeat_instrument

    if "consent_date" in record and "consent_status" in record:
        return "consent_records"
    if "referral_id" in record or ("destination" in record and "follow_up_date" in record):
        return "referrals"
    if "screening_date" in record and "distress_score" in record:
        return "distress_screenings"
    if "session_number" in record and "attendance" in record:
        return "wp6_sessions"
    if "country" in record and "enrollment_date" in record:
        return "participants"

    return "survey_responses"


def normalize_record(record: dict[str, Any], *, source_mode: str) -> dict[str, Any]:
    return {k: ("" if v is None else v) for k, v in record.items() if not k.startswith("_")}


def _coerce_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _survey_month(record: dict[str, Any]) -> int | None:
    if month := _coerce_int(record.get("month")):
        return month

    event_name = str(record.get("redcap_event_name", ""))
    if event_name == "baseline_arm_1":
        return 0

    match = re.search(r"month_(\d+)_arm_1", event_name)
    if match:
        return int(match.group(1))

    return _coerce_int(record.get("redcap_repeat_instance"))


def _merge_non_blank(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if value not in (None, ""):
            target[key] = value
        elif key not in target:
            target[key] = value


def group_records_by_instrument(
    records: list[dict[str, Any]],
    *,
    source_mode: str,
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    survey_index: dict[tuple[str, int | None], dict[str, Any]] = {}

    for record in records:
        entity = route_record_to_instrument(record)
        normalized = normalize_record(record, source_mode=source_mode)

        if entity == "survey_responses":
            normalized["month"] = _survey_month(normalized)
            key = (str(normalized.get("record_id", "")), normalized.get("month"))
            if key in survey_index:
                _merge_non_blank(survey_index[key], normalized)
            else:
                survey_index[key] = normalized
                grouped.setdefault(entity, []).append(normalized)
            continue

        grouped.setdefault(entity, []).append(normalized)

    return grouped
