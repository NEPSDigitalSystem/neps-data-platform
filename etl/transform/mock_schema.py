from __future__ import annotations

from etl.models.metadata import FieldDefinition, InstrumentDefinition


BACKEND_ENTITIES: dict[str, InstrumentDefinition] = {
    "participants": InstrumentDefinition(
        instrument_name="participants",
        instrument_label="Participants",
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("country", "text"),
            FieldDefinition("site", "text"),
            FieldDefinition("school", "text"),
            FieldDefinition("age", "integer"),
            FieldDefinition("gender", "text"),
            FieldDefinition("grade_level", "text"),
            FieldDefinition("enrollment_date", "date"),
            FieldDefinition("phone_contact", "text"),
        ],
    ),
    "consent_records": InstrumentDefinition(
        instrument_name="consent_records",
        instrument_label="Consent Records",
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("consent_date", "date"),
            FieldDefinition("consent_version", "text"),
            FieldDefinition("consent_status", "text"),
            FieldDefinition("guardian_consent", "text"),
            FieldDefinition("assent_status", "text"),
            FieldDefinition("consent_withdrawn", "text"),
            FieldDefinition("withdrawal_reason", "text"),
            FieldDefinition("re_consent_required", "text"),
            FieldDefinition("re_consent_date", "date"),
        ],
    ),
    "survey_responses": InstrumentDefinition(
        instrument_name="survey_responses",
        instrument_label="Survey Responses",
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("month", "integer"),
            FieldDefinition("survey_date", "date"),
            FieldDefinition("survey_complete", "text"),
            FieldDefinition("perceived_stress_score", "float"),
            FieldDefinition("anxiety_score", "float"),
            FieldDefinition("depression_score", "float"),
            FieldDefinition("suicidality_screening", "text"),
            FieldDefinition("risk_flag", "text"),
            FieldDefinition("resilience_score", "float"),
            FieldDefinition("social_support", "float"),
            FieldDefinition("internalised_stigma", "float"),
        ],
    ),
    "distress_screenings": InstrumentDefinition(
        instrument_name="distress_screenings",
        instrument_label="Distress Screenings",
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("screening_date", "date"),
            FieldDefinition("distress_score", "float"),
            FieldDefinition("suicidality_flag", "text"),
            FieldDefinition("severity", "text"),
            FieldDefinition("trigger_form", "text"),
            FieldDefinition("assigned_responder", "text"),
            FieldDefinition("action_taken", "text"),
            FieldDefinition("referral_made", "text"),
            FieldDefinition("welfare_check_due", "date"),
            FieldDefinition("resolution_status", "text"),
        ],
    ),
    "referrals": InstrumentDefinition(
        instrument_name="referrals",
        instrument_label="Referrals",
        fields=[
            FieldDefinition("referral_id", "text"),
            FieldDefinition("record_id", "text"),
            FieldDefinition("initiation_date", "date"),
            FieldDefinition("destination", "text"),
            FieldDefinition("status", "text"),
            FieldDefinition("notes", "text"),
            FieldDefinition("follow_up_date", "date"),
        ],
    ),
    "wp6_sessions": InstrumentDefinition(
        instrument_name="wp6_sessions",
        instrument_label="WP6 Sessions",
        repeating=True,
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("session_number", "integer"),
            FieldDefinition("session_date", "date"),
            FieldDefinition("attendance", "text"),
            FieldDefinition("engagement_level", "float"),
            FieldDefinition("fidelity_score", "float"),
            FieldDefinition("distress_pre", "float"),
            FieldDefinition("distress_post", "float"),
        ],
    ),
}

# Backwards-compatible name used by older tests and imports.
MOCK_INSTRUMENTS = BACKEND_ENTITIES


def get_backend_instruments() -> list[InstrumentDefinition]:
    return list(BACKEND_ENTITIES.values())


def get_mock_instruments() -> list[InstrumentDefinition]:
    return get_backend_instruments()
