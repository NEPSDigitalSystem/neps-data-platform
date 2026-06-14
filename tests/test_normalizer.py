from __future__ import annotations

from etl.transform.normalizer import group_records_by_instrument, route_record_to_instrument


def test_route_record_to_instrument() -> None:
<<<<<<< Updated upstream
    assert route_record_to_instrument({"_instrument": "wp6_session"}) == "wp6_sessions"
    assert route_record_to_instrument({"redcap_repeat_instrument": "comprehensive_wave"}) == "survey_responses"
    assert route_record_to_instrument({"country": "Ghana", "enrollment_date": "2025-01-01"}) == "participants"
    assert route_record_to_instrument({"consent_date": "2025-01-01", "consent_status": "consented"}) == "consent_records"
=======
    assert route_record_to_instrument({"_instrument": "wp6_session"}) == "wp6_session"
    assert route_record_to_instrument({"redcap_repeat_instrument": "comprehensive_wave"}) == "comprehensive_wave"
    assert route_record_to_instrument({"country": "Ghana", "cohort_status": "active"}) == "demographics"
>>>>>>> Stashed changes


def test_group_records_by_instrument(mock_records) -> None:
    grouped = group_records_by_instrument(mock_records, source_mode="mock")
<<<<<<< Updated upstream
    assert "survey_responses" in grouped
    assert len(grouped["survey_responses"]) == 1
    assert grouped["survey_responses"][0]["month"] == 1


def test_group_records_merges_comprehensive_wave_into_survey_response() -> None:
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
            "social_support": 18.0,
            "internalised_stigma": 2.0,
            "redcap_repeat_instrument": "comprehensive_wave",
            "redcap_repeat_instance": "1",
        },
    ]

    grouped = group_records_by_instrument(records, source_mode="mock")

    assert len(grouped["survey_responses"]) == 1
    row = grouped["survey_responses"][0]
    assert row["anxiety_score"] == 8.0
    assert row["resilience_score"] == 72.5
    assert row["month"] == 6
=======
    assert "monthly_self_report" in grouped
    assert len(grouped["monthly_self_report"]) == 1
>>>>>>> Stashed changes
