from __future__ import annotations

from etl.models.metadata import FieldDefinition, InstrumentDefinition

<<<<<<< Updated upstream

BACKEND_ENTITIES: dict[str, InstrumentDefinition] = {
    "participants": InstrumentDefinition(
        instrument_name="participants",
        instrument_label="Participants",
        fields=[
            FieldDefinition("record_id", "text"),
=======
MOCK_INSTRUMENTS: dict[str, InstrumentDefinition] = {
    "demographics": InstrumentDefinition(
        instrument_name="demographics",
        instrument_label="Demographics",
        repeating=False,
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("redcap_event_name", "text"),
>>>>>>> Stashed changes
            FieldDefinition("country", "text"),
            FieldDefinition("site", "text"),
            FieldDefinition("school", "text"),
            FieldDefinition("age", "integer"),
<<<<<<< Updated upstream
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
=======
            FieldDefinition("date_of_birth", "date"),
            FieldDefinition("gender", "text"),
            FieldDefinition("grade_level", "text"),
            FieldDefinition("enrollment_date", "date"),
            FieldDefinition("cohort_status", "text"),
            FieldDefinition("phone_contact", "text"),
            FieldDefinition("consent_status", "text"),
            FieldDefinition("redcap_data_access_group", "text"),
        ],
    ),
    "monthly_self_report": InstrumentDefinition(
        instrument_name="monthly_self_report",
        instrument_label="Monthly Self-Report",
        repeating=True,
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("redcap_event_name", "text"),
>>>>>>> Stashed changes
            FieldDefinition("month", "integer"),
            FieldDefinition("survey_date", "date"),
            FieldDefinition("survey_complete", "text"),
            FieldDefinition("perceived_stress_score", "float"),
<<<<<<< Updated upstream
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
=======
            FieldDefinition("mood_status", "text"),
            FieldDefinition("anxiety_score", "float"),
            FieldDefinition("depression_score", "float"),
            FieldDefinition("sleep_quality", "text"),
            FieldDefinition("daily_functioning", "float"),
            FieldDefinition("fatigue_level", "text"),
            FieldDefinition("school_attendance_days", "integer"),
            FieldDefinition("social_isolation_score", "float"),
            FieldDefinition("coping_behaviours", "text"),
            FieldDefinition("substance_use", "text"),
            FieldDefinition("suicidality_screening", "text"),
            FieldDefinition("self_esteem_score", "float"),
            FieldDefinition("loneliness_score", "float"),
            FieldDefinition("risk_flag", "text"),
            FieldDefinition("requires_follow_up", "text"),
            FieldDefinition("redcap_repeat_instrument", "text"),
            FieldDefinition("redcap_repeat_instance", "text"),
        ],
    ),
    "comprehensive_wave": InstrumentDefinition(
        instrument_name="comprehensive_wave",
        instrument_label="Comprehensive Survey Wave",
        repeating=True,
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("redcap_event_name", "text"),
            FieldDefinition("wave_type", "text"),
            FieldDefinition("survey_complete", "text"),
            FieldDefinition("examination_stress", "float"),
            FieldDefinition("academic_pressure", "float"),
            FieldDefinition("homework_burden", "float"),
            FieldDefinition("school_climate", "text"),
            FieldDefinition("bullying_exposure", "text"),
            FieldDefinition("harsh_discipline", "text"),
            FieldDefinition("educational_aspirations", "text"),
            FieldDefinition("fear_of_failure", "float"),
            FieldDefinition("teacher_support", "float"),
            FieldDefinition("counselling_access", "text"),
            FieldDefinition("household_assets", "integer"),
            FieldDefinition("food_insecurity", "text"),
            FieldDefinition("economic_strain", "float"),
            FieldDefinition("employment_pressure", "text"),
            FieldDefinition("financial_stress", "float"),
            FieldDefinition("digital_access", "text"),
            FieldDefinition("household_instability", "text"),
            FieldDefinition("internalised_stigma", "float"),
            FieldDefinition("community_stigma", "float"),
            FieldDefinition("family_stigma", "float"),
            FieldDefinition("school_stigma", "float"),
            FieldDefinition("mental_health_literacy", "float"),
            FieldDefinition("help_seeking_intention", "text"),
            FieldDefinition("help_seeking_behaviour", "text"),
            FieldDefinition("awareness_of_services", "text"),
            FieldDefinition("resilience_score", "float"),
            FieldDefinition("social_support", "float"),
            FieldDefinition("family_connectedness", "float"),
            FieldDefinition("peer_support", "float"),
            FieldDefinition("community_connectedness", "float"),
            FieldDefinition("religious_support", "float"),
            FieldDefinition("school_belonging", "float"),
            FieldDefinition("redcap_repeat_instrument", "text"),
            FieldDefinition("redcap_repeat_instance", "text"),
        ],
    ),
    "distress_screening": InstrumentDefinition(
        instrument_name="distress_screening",
        instrument_label="Distress Screening",
        repeating=False,
>>>>>>> Stashed changes
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("screening_date", "date"),
            FieldDefinition("distress_score", "float"),
            FieldDefinition("suicidality_flag", "text"),
            FieldDefinition("severity", "text"),
            FieldDefinition("trigger_form", "text"),
<<<<<<< Updated upstream
            FieldDefinition("assigned_responder", "text"),
            FieldDefinition("action_taken", "text"),
            FieldDefinition("referral_made", "text"),
=======
            FieldDefinition("trigger_item", "text"),
            FieldDefinition("assigned_responder", "text"),
            FieldDefinition("action_taken", "text"),
            FieldDefinition("referral_made", "text"),
            FieldDefinition("referral_destination", "text"),
>>>>>>> Stashed changes
            FieldDefinition("welfare_check_due", "date"),
            FieldDefinition("resolution_status", "text"),
        ],
    ),
<<<<<<< Updated upstream
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
=======
    "wp6_session": InstrumentDefinition(
        instrument_name="wp6_session",
        instrument_label="WP6 Session Record",
>>>>>>> Stashed changes
        repeating=True,
        fields=[
            FieldDefinition("record_id", "text"),
            FieldDefinition("session_number", "integer"),
            FieldDefinition("session_date", "date"),
            FieldDefinition("attendance", "text"),
            FieldDefinition("engagement_level", "float"),
            FieldDefinition("fidelity_score", "float"),
<<<<<<< Updated upstream
            FieldDefinition("distress_pre", "float"),
            FieldDefinition("distress_post", "float"),
=======
            FieldDefinition("satisfaction_score", "float"),
            FieldDefinition("homework_completion", "text"),
            FieldDefinition("distress_pre", "float"),
            FieldDefinition("distress_post", "float"),
            FieldDefinition("redcap_repeat_instrument", "text"),
            FieldDefinition("redcap_repeat_instance", "text"),
>>>>>>> Stashed changes
        ],
    ),
}

<<<<<<< Updated upstream
# Backwards-compatible name used by older tests and imports.
MOCK_INSTRUMENTS = BACKEND_ENTITIES


def get_backend_instruments() -> list[InstrumentDefinition]:
    return list(BACKEND_ENTITIES.values())


def get_mock_instruments() -> list[InstrumentDefinition]:
    return get_backend_instruments()
=======

def get_mock_instruments() -> list[InstrumentDefinition]:
    return list(MOCK_INSTRUMENTS.values())
>>>>>>> Stashed changes
