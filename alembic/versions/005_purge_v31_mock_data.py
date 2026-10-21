"""Purge V3.1 mock data before production REDCap ingestion.

Removes all mock/synthetic V3.1 rows so a production deployment starts from a
clean store. Applying this revision deletes data; it is a deliberate switch
away from the mock source, not a routine schema step.

Revision ID: 005_purge_v31_mock_data
Revises: 004_storage_integrity
Create Date: 2026-10-20
"""
from alembic import op
from sqlalchemy import text

revision = "005_purge_v31_mock_data"
down_revision = "004_storage_integrity"
branch_labels = None
depends_on = None

# Child tables first so the truncate order never depends on CASCADE alone.
PURGE_ORDER = (
    "nds_v31_derived",
    "nds_v31_validated",
    "nds_v31_audit",
    "nds_v31_source",
    "nds_v31_intake_pending",
    "nds_v31_intake_head",
    "nds_v31_intake_audit",
    "nds_v31_intake_raw",
    "nds_v31_participant_links",
)


def upgrade() -> None:
    for table in PURGE_ORDER:
        op.execute(text(f"TRUNCATE TABLE {table} CASCADE"))


def downgrade() -> None:
    raise PermissionError("Purged mock data cannot be restored; replay from source instead")
