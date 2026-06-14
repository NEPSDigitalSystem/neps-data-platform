from __future__ import annotations

import responses

from etl.extract.metadata_normalizer import normalize_metadata
from etl.extract.mock_client import MockRedcapClient


@responses.activate
def test_mock_client_export_metadata(mock_settings, mock_metadata) -> None:
    responses.add(
        responses.GET,
        "http://mock-redcap.test/api/redcap/export/metadata",
        json=mock_metadata,
    )

    client = MockRedcapClient(mock_settings)
    metadata = client.export_metadata()

    assert metadata.project_id == "NEPS-2025"
    assert len(metadata.instruments) == 6
    assert metadata.get_instrument("participants") is not None
    assert metadata.source_mode == "mock"


@responses.activate
def test_mock_client_export_records_aggregates_sources(mock_settings, mock_records) -> None:
    responses.add(
        responses.GET,
        "http://mock-redcap.test/api/redcap/export/records",
        json=mock_records,
    )
    responses.add(
        responses.GET,
        "http://mock-redcap.test/api/redcap/participants",
        json={
            "data": [
                {
                    "record_id": "NEPS-GHA-0001",
                    "redcap_event_name": "baseline_arm_1",
                    "country": "Ghana",
                    "site": "Kumasi",
                    "school": "KNUST SHS",
                    "age": 16,
                    "date_of_birth": "2009-01-01",
                    "gender": "Female",
                    "grade_level": "10",
                    "enrollment_date": "2025-01-01",
                    "cohort_status": "active",
                    "phone_contact": "+233200000000",
                    "consent_status": "consented",
                    "redcap_data_access_group": "kumasi",
                }
            ],
            "total": 1,
        },
    )
    responses.add(
        responses.GET,
        "http://mock-redcap.test/api/redcap/participants/NEPS-GHA-0001/consent",
        json={
            "record_id": "NEPS-GHA-0001",
            "consent_date": "2025-01-01",
            "consent_version": "v1.0",
            "consent_status": "consented",
            "guardian_consent": "Yes",
            "assent_status": "Yes",
            "consent_withdrawn": "0",
            "withdrawal_reason": "",
            "re_consent_required": "0",
            "re_consent_date": "",
        },
    )
    responses.add(
        responses.GET,
        "http://mock-redcap.test/api/redcap/screenings/distress",
        json={
            "screenings": [
                {
                    "record_id": "NEPS-GHA-0001",
                    "screening_date": "2025-03-01",
                    "distress_score": 20.0,
                    "suicidality_flag": "1",
                    "severity": "high",
                    "trigger_form": "monthly_self_report",
                    "trigger_item": "suicidality_screening",
                    "assigned_responder": "Counselor A",
                    "action_taken": "",
                    "referral_made": "0",
                    "referral_destination": "",
                    "welfare_check_due": "2025-03-02",
                    "resolution_status": "open",
                }
            ]
        },
    )
    responses.add(
        responses.GET,
        "http://mock-redcap.test/api/redcap/referrals",
        json={
            "referrals": [
                {
                    "referral_id": "REF-0001",
                    "record_id": "NEPS-GHA-0001",
                    "initiation_date": "2025-03-01",
                    "destination": "Counseling Unit",
                    "status": "initiated",
                    "notes": "Follow up required",
                    "follow_up_date": "2025-03-08",
                }
            ],
            "count": 1,
        },
    )
    responses.add(
        responses.GET,
        "http://mock-redcap.test/api/redcap/wp6/sessions/NEPS-GHA-0001",
        json={
            "record_id": "NEPS-GHA-0001",
            "sessions": [
                {
                    "record_id": "NEPS-GHA-0001",
                    "session_number": 1,
                    "session_date": "2025-01-15",
                    "attendance": "Present",
                    "engagement_level": 4.5,
                    "fidelity_score": 90.0,
                    "satisfaction_score": 4.0,
                    "homework_completion": "Complete",
                    "distress_pre": 18.0,
                    "distress_post": 10.0,
                }
            ],
        },
    )

    client = MockRedcapClient(mock_settings)
    records = client.export_records()

    entities = {record["_entity"] for record in records}
    assert "participants" in entities
    assert "consent_records" in entities
    assert "survey_responses" in entities
    assert "distress_screenings" in entities
    assert "referrals" in entities
    assert "wp6_sessions" in entities


def test_normalize_mock_metadata(mock_metadata) -> None:
    metadata = normalize_metadata(mock_metadata, source_mode="mock")
    assert metadata.metadata_hash()
    assert metadata.get_instrument("participants") is not None
