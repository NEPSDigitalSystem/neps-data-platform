"""Add missing nullable legacy columns without changing retained values."""
from alembic import op

revision = "003_legacy_columns"
down_revision = "002_independent_source_intake"
branch_labels = None
depends_on = None

COLUMNS = {
    "raw_redcap_demographics": {
        "employment_status": "TEXT", "food_security": "TEXT",
        "healthcare_access": "TEXT", "socioeconomic_status": "TEXT",
    },
    "raw_redcap_monthly_self_report": {
        "mood_score": "DOUBLE PRECISION", "sleep_quality_score": "DOUBLE PRECISION",
        "fatigue_score": "DOUBLE PRECISION", "attendance_score": "DOUBLE PRECISION",
        "coping_score": "DOUBLE PRECISION", "substance_abuse_score": "DOUBLE PRECISION",
        "suicidality_score": "DOUBLE PRECISION",
    },
}


def upgrade():
    for table, columns in COLUMNS.items():
        for column, kind in columns.items():
            op.execute(f'ALTER TABLE redcap.{table} ADD COLUMN IF NOT EXISTS {column} {kind}')
            # Existing manual repairs must have compatible types. Do not
            # silently accept a differently typed column or cast retained data.
            expected = 'text' if kind == 'TEXT' else 'double precision'
            op.execute(f"""DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'redcap' AND table_name = '{table}'
                    AND column_name = '{column}' AND data_type = '{expected}') THEN
                    RAISE EXCEPTION 'Legacy column type requires reviewed repair';
                END IF;
            END $$""")


def downgrade():
    raise PermissionError("Retained legacy columns cannot be dropped by automatic downgrade")
