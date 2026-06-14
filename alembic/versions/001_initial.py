"""Initial control tables and normalized REDCap sync tables.

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
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
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
        CREATE TABLE IF NOT EXISTS redcap.participants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            record_id TEXT NOT NULL UNIQUE,
            country TEXT,
            site TEXT,
            school TEXT,
            age INTEGER,
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
        )
        """
    )

    op.execute(
        """
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
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS redcap.distress_screenings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            record_id TEXT NOT NULL REFERENCES redcap.participants(record_id),
            screening_date DATE NOT NULL,
            distress_score DOUBLE PRECISION,
            suicidality_flag TEXT,
            severity TEXT,
            trigger_form TEXT,
            assigned_responder TEXT,
            action_taken TEXT,
            referral_made TEXT,
            welfare_check_due DATE,
            resolution_status TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (record_id, screening_date)
        )
        """
    )

    op.execute(
        """
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
            session_date DATE,
            attendance TEXT,
            engagement_level DOUBLE PRECISION,
            fidelity_score DOUBLE PRECISION,
            distress_pre DOUBLE PRECISION,
            distress_post DOUBLE PRECISION,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (record_id, session_number)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS redcap CASCADE")
