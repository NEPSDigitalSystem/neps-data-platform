"""Four-table SQLAlchemy helper for local synthetic repository tests.

The active Alembic chain 002 through 004 owns the full nine-table warehouse
schema, including intake and participant links. This helper does not replace
that chain or provision its schema. Live permissions and deployment acceptance
remain external. Never use legacy downgrade (DROP SCHEMA CASCADE) for recovery.
"""
from .v31 import metadata


def upgrade(connection):
    metadata.create_all(connection, checkfirst=True)


def downgrade(connection, *, disposable_synthetic_database=False):
    if not disposable_synthetic_database:
        raise PermissionError('Recovery backup and explicit authorisation required')
    metadata.drop_all(connection, checkfirst=True)
