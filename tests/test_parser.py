from __future__ import annotations

from etl.transform.mock_schema import MOCK_INSTRUMENTS
from etl.transform.parser import prepare_row, record_conflict_keys


def test_prepare_row_keeps_backend_schema_columns_only() -> None:
    instrument = MOCK_INSTRUMENTS["participants"]
    row = prepare_row(
        {
            "record_id": "NEPS-GHA-0001",
            "country": "Ghana",
            "cohort_status": "active",
            "_entity": "participants",
        },
        instrument,
        synced_at="2025-01-01T00:00:00Z",
        etl_run_id="run-1",
        source_mode="mock",
    )

    assert row == {"record_id": "NEPS-GHA-0001", "country": "Ghana"}


def test_record_conflict_keys_match_backend_entities() -> None:
    assert record_conflict_keys(MOCK_INSTRUMENTS["participants"]) == ["record_id"]
    assert record_conflict_keys(MOCK_INSTRUMENTS["survey_responses"]) == ["record_id", "month"]
    assert record_conflict_keys(MOCK_INSTRUMENTS["wp6_sessions"]) == ["record_id", "session_number"]
