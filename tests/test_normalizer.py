from __future__ import annotations

from etl.transform.mock_schema import MOCK_INSTRUMENTS
from etl.transform.normalizer import group_records_by_instrument, route_record_to_instrument


def test_route_record_to_instrument() -> None:
    assert route_record_to_instrument({"_instrument": "wp6_session"}) == "wp6_session"
    assert route_record_to_instrument({"redcap_repeat_instrument": "comprehensive_wave"}) == "comprehensive_wave"
    assert route_record_to_instrument({"country": "Ghana", "cohort_status": "active"}) == "demographics"
    assert route_record_to_instrument({"screening_date": "2025-01-01", "distress_score": 5.0}) == "distress_screening"


def test_group_records_by_instrument(mock_records) -> None:
    grouped = group_records_by_instrument(mock_records, source_mode="mock")
    assert "monthly_self_report" in grouped
    assert len(grouped["monthly_self_report"]) == 1


def test_group_records_keeps_separate_instruments() -> None:
    records = [
        {
            "record_id": "NEPS-GHA-0001",
            "redcap_event_name": "month_6_arm_1",
            "month": 6,
            "anxiety_score": 8.0,
            "redcap_repeat_instrument": "monthly_self_report",
            "redcap_repeat_instance": "6",
        },
        {
            "record_id": "NEPS-GHA-0001",
            "redcap_event_name": "month_6_arm_1",
            "resilience_score": 72.5,
            "redcap_repeat_instrument": "comprehensive_wave",
            "redcap_repeat_instance": "1",
        },
    ]

    grouped = group_records_by_instrument(records, source_mode="mock")

    assert "monthly_self_report" in grouped
    assert "comprehensive_wave" in grouped
    assert len(grouped["monthly_self_report"]) == 1
    assert grouped["monthly_self_report"][0]["anxiety_score"] == 8.0
    assert grouped["comprehensive_wave"][0]["resilience_score"] == 72.5
