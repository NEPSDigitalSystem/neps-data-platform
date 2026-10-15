"""Additive candidate schema, deliberately not registered in active Alembic.

Existing 001_initial owns PostgreSQL redcap schema and legacy tables; these
four nds_v31_* tables do not alter them. Production schema selection, trusted
adapters, encryption/roles/backup and PostgreSQL DDL review remain gated.
Never use legacy downgrade (DROP SCHEMA CASCADE) for this candidate.
"""
from .v31 import metadata


def upgrade(connection):
    metadata.create_all(connection, checkfirst=True)


def downgrade(connection, *, disposable_synthetic_database=False):
    if not disposable_synthetic_database:
        raise PermissionError('Recovery backup and explicit authorisation required')
    metadata.drop_all(connection, checkfirst=True)
