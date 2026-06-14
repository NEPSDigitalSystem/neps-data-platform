<<<<<<< Updated upstream
"""Initial control tables and normalized REDCap sync tables.
=======
"""Initial control tables and raw landing tables.
>>>>>>> Stashed changes

Revision ID: 001_initial
Revises:
Create Date: 2026-06-08
"""

from __future__ import annotations

from alembic import op

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
<<<<<<< Updated upstream
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
=======
>>>>>>> Stashed changes
    op.execute("CREATE SCHEMA IF NOT EXISTS redcap")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS redcap.etl_sync_state (
            project_id TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            metadata_hash TEXT,
            source_mode TEXT NOT NULL,
            last_modified_at TIMESTAMPTZ,
            last_run_at TIMESTAMPTZ,
            PRIMARY KEY (project_id, entity_name)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS redcap.etl_run_log (
            run_id UUID PRIMARY KEY,
            started_at TIMESTAMPTZ NOT NULL,
            finished_at TIMESTAMPTZ,
            status TEXT NOT NULL,
            source_mode TEXT NOT NULL,
            project_id TEXT NOT NULL,
            sync_type TEXT NOT NULL,
            records_extracted INTEGER DEFAULT 0,
            records_loaded INTEGER DEFAULT 0,
            error_message TEXT
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS redcap.raw_redcap_metadata (
            project_id TEXT PRIMARY KEY,
            metadata_json JSONB NOT NULL,
            metadata_hash TEXT NOT NULL,
            source_mode TEXT NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
<<<<<<< Updated upstream
        CREATE TABLE IF NOT EXISTS redcap.participants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            record_id TEXT NOT NULL UNIQUE,
=======
        CREATE TABLE IF NOT EXISTS redcap.raw_redcap_demographics (
            record_id TEXT NOT NULL,
            redcap_event_name TEXT,
>>>>>>> Stashed changes
            country TEXT,
            site TEXT,
            school TEXT,
            age INTEGER,
<<<<<<< Updated upstream
            gender TEXT,
            grade_level TEXT,
            enrollment_date DATE,
            phone_contact TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS redcap.consent_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            participant_id UUID NOT NULL REFERENCES redcap.participants(id),
            record_id TEXT NOT NULL REFERENCES redcap.participants(record_id),
            consent_date DATE,
            consent_version TEXT,
            consent_status TEXT,
            guardian_consent TEXT,
            assent_status TEXT,
            consent_withdrawn TEXT,
            withdrawal_reason TEXT,
            re_consent_required TEXT,
            re_consent_date DATE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (record_id)
=======
            date_of_birth DATE,
            gender TEXT,
            grade_level TEXT,
            enrollment_date DATE,
            cohort_status TEXT,
            phone_contact TEXT,
            consent_status TEXT,
            redcap_data_access_group TEXT,
            _synced_at TIMESTAMPTZ,
            _etl_run_id UUID,
            _source_mode TEXT,
            PRIMARY KEY (record_id, redcap_event_name)
>>>>>>> Stashed changes
        )
        """
    )

    op.execute(
        """
<<<<<<< Updated upstream
        CREATE TABLE IF NOT EXISTS redcap.survey_responses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            record_id TEXT NOT NULL REFERENCES redcap.participants(record_id),
            month INTEGER NOT NULL,
            survey_date DATE,
            survey_complete TEXT,
            perceived_stress_score DOUBLE PRECISION,
            anxiety_score DOUBLE PRECISION,
            depression_score DOUBLE PRECISION,
            suicidality_screening TEXT,
            risk_flag TEXT,
            resilience_score DOUBLE PRECISION,
            social_support DOUBLE PRECISION,
            internalised_stigma DOUBLE PRECISION,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (record_id, month)
=======
        CREATE TABLE IF NOT EXISTS redcap.raw_redcap_monthly_self_report (
            record_id TEXT NOT NULL,
            redcap_event_name TEXT,
            month INTEGER,
            survey_date DATE,
            survey_complete TEXT,
            perceived_stress_score DOUBLE PRECISION,
            mood_status TEXT,
            anxiety_score DOUBLE PRECISION,
            depression_score DOUBLE PRECISION,
            sleep_quality TEXT,
            daily_functioning DOUBLE PRECISION,
            fatigue_level TEXT,
            school_attendance_days INTEGER,
            social_isolation_score DOUBLE PRECISION,
            coping_behaviours TEXT,
            substance_use TEXT,
            suicidality_screening TEXT,
            self_esteem_score DOUBLE PRECISION,
            loneliness_score DOUBLE PRECISION,
            risk_flag TEXT,
            requires_follow_up TEXT,
            redcap_repeat_instrument TEXT,
            redcap_repeat_instance TEXT,
            _synced_at TIMESTAMPTZ,
            _etl_run_id UUID,
            _source_mode TEXT,
            PRIMARY KEY (record_id, redcap_event_name, redcap_repeat_instrument, redcap_repeat_instance)
>>>>>>> Stashed changes
        )
        """
    )

    op.execute(
        """
<<<<<<< Updated upstream
        CREATE TABLE IF NOT EXISTS redcap.distress_screenings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            record_id TEXT NOT NULL REFERENCES redcap.participants(record_id),
            screening_date DATE NOT NULL,
=======
        CREATE TABLE IF NOT EXISTS redcap.raw_redcap_comprehensive_wave (
            record_id TEXT NOT NULL,
            redcap_event_name TEXT,
            wave_type TEXT,
            survey_complete TEXT,
            examination_stress DOUBLE PRECISION,
            academic_pressure DOUBLE PRECISION,
            homework_burden DOUBLE PRECISION,
            school_climate TEXT,
            bullying_exposure TEXT,
            harsh_discipline TEXT,
            educational_aspirations TEXT,
            fear_of_failure DOUBLE PRECISION,
            teacher_support DOUBLE PRECISION,
            counselling_access TEXT,
            household_assets INTEGER,
            food_insecurity TEXT,
            economic_strain DOUBLE PRECISION,
            employment_pressure TEXT,
            financial_stress DOUBLE PRECISION,
            digital_access TEXT,
            household_instability TEXT,
            internalised_stigma DOUBLE PRECISION,
            community_stigma DOUBLE PRECISION,
            family_stigma DOUBLE PRECISION,
            school_stigma DOUBLE PRECISION,
            mental_health_literacy DOUBLE PRECISION,
            help_seeking_intention TEXT,
            help_seeking_behaviour TEXT,
            awareness_of_services TEXT,
            resilience_score DOUBLE PRECISION,
            social_support DOUBLE PRECISION,
            family_connectedness DOUBLE PRECISION,
            peer_support DOUBLE PRECISION,
            community_connectedness DOUBLE PRECISION,
            religious_support DOUBLE PRECISION,
            school_belonging DOUBLE PRECISION,
            redcap_repeat_instrument TEXT,
            redcap_repeat_instance TEXT,
            _synced_at TIMESTAMPTZ,
            _etl_run_id UUID,
            _source_mode TEXT,
            PRIMARY KEY (record_id, redcap_event_name, redcap_repeat_instrument, redcap_repeat_instance)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS redcap.raw_redcap_distress_screening (
            record_id TEXT NOT NULL,
            screening_date DATE,
>>>>>>> Stashed changes
            distress_score DOUBLE PRECISION,
            suicidality_flag TEXT,
            severity TEXT,
            trigger_form TEXT,
<<<<<<< Updated upstream
            assigned_responder TEXT,
            action_taken TEXT,
            referral_made TEXT,
            welfare_check_due DATE,
            resolution_status TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (record_id, screening_date)
=======
            trigger_item TEXT,
            assigned_responder TEXT,
            action_taken TEXT,
            referral_made TEXT,
            referral_destination TEXT,
            welfare_check_due DATE,
            resolution_status TEXT,
            _synced_at TIMESTAMPTZ,
            _etl_run_id UUID,
            _source_mode TEXT,
            PRIMARY KEY (record_id, screening_date)
>>>>>>> Stashed changes
        )
        """
    )

    op.execute(
        """
<<<<<<< Updated upstream
        CREATE TABLE IF NOT EXISTS redcap.referrals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            referral_id TEXT NOT NULL UNIQUE,
            record_id TEXT NOT NULL REFERENCES redcap.participants(record_id),
            initiation_date DATE,
            destination TEXT,
            status TEXT,
            notes TEXT,
            follow_up_date DATE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS redcap.wp6_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            record_id TEXT NOT NULL REFERENCES redcap.participants(record_id),
            session_number INTEGER NOT NULL,
=======
        CREATE TABLE IF NOT EXISTS redcap.raw_redcap_wp6_session (
            record_id TEXT NOT NULL,
            session_number INTEGER,
>>>>>>> Stashed changes
            session_date DATE,
            attendance TEXT,
            engagement_level DOUBLE PRECISION,
            fidelity_score DOUBLE PRECISION,
<<<<<<< Updated upstream
            distress_pre DOUBLE PRECISION,
            distress_post DOUBLE PRECISION,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (record_id, session_number)
=======
            satisfaction_score DOUBLE PRECISION,
            homework_completion TEXT,
            distress_pre DOUBLE PRECISION,
            distress_post DOUBLE PRECISION,
            redcap_repeat_instrument TEXT,
            redcap_repeat_instance TEXT,
            _synced_at TIMESTAMPTZ,
            _etl_run_id UUID,
            _source_mode TEXT,
            PRIMARY KEY (record_id, redcap_repeat_instrument, redcap_repeat_instance)
>>>>>>> Stashed changes
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS redcap CASCADE")
