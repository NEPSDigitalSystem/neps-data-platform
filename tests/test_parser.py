from __future__ import annotations

from etl.transform.mock_schema import MOCK_INSTRUMENTS
from etl.transform.parser import prepare_row, record_conflict_keys


def test_prepare_row_adds_audit_columns() -> None:
    instrument = MOCK_INSTRUMENTS["demographics"]
    row = prepare_row(
        {"record_id": "NEPS-GHA-0001", "country": "Ghana"},
        instrument,
        synced_at="2025-01-01T00:00:00Z",
        etl_run_id="run-1",
        source_mode="mock",
    )

    assert row["record_id"] == "NEPS-GHA-0001"
    assert row["_source_mode"] == "mock"
    assert row["_etl_run_id"] == "run-1"


def test_prepare_row_keeps_instrument_columns_only() -> None:
    instrument = MOCK_INSTRUMENTS["demographics"]
    row = prepare_row(
        {
            "record_id": "NEPS-GHA-0001",
            "country": "Ghana",
            "cohort_status": "active",
            "_instrument": "demographics",
        },
        instrument,
        synced_at="2025-01-01T00:00:00Z",
        etl_run_id="run-1",
        source_mode="mock",
    )

    assert "_instrument" not in row
    assert row["record_id"] == "NEPS-GHA-0001"
    assert row["_source_mode"] == "mock"


def test_record_conflict_keys_repeating() -> None:
    assert record_conflict_keys(MOCK_INSTRUMENTS["monthly_self_report"]) == [
        "record_id",
        "redcap_event_name",
        "redcap_repeat_instrument",
        "redcap_repeat_instance",
    ]


def test_record_conflict_keys_non_repeating() -> None:
    assert record_conflict_keys(MOCK_INSTRUMENTS["demographics"]) == ["record_id", "redcap_event_name"]


def test_record_conflict_keys_distress() -> None:
    assert record_conflict_keys(MOCK_INSTRUMENTS["distress_screening"]) == ["record_id", "screening_date"]
