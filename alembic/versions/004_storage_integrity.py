"""Scope research revisions by destination and bind intake heads to revisions."""
from alembic import op

revision = "004_storage_integrity"
down_revision = "003_legacy_columns"
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE nds_v31_source ADD CONSTRAINT uq_source_destination_revision '
               'UNIQUE (identity_key, storage_destination, revision)')
    op.execute('ALTER TABLE nds_v31_source DROP CONSTRAINT nds_v31_source_identity_key_revision_key')
    op.execute('ALTER TABLE nds_v31_intake_raw ADD CONSTRAINT uq_intake_head_target '
               'UNIQUE (identity_key, revision, id)')
    op.execute('ALTER TABLE nds_v31_intake_head ADD CONSTRAINT fk_intake_head_revision '
               'FOREIGN KEY (identity_key, revision, source_revision_id) '
               'REFERENCES nds_v31_intake_raw (identity_key, revision, id)')
    for table in ['nds_v31_intake_raw', 'nds_v31_intake_head', 'nds_v31_source']:
        op.execute(f'ALTER TABLE {table} ADD CONSTRAINT ck_{table}_revision CHECK (revision > 0)')
    op.execute("ALTER TABLE nds_v31_intake_raw ADD CONSTRAINT ck_intake_project "
               "CHECK ((identity->>'project') IS NOT DISTINCT FROM project)")
    op.execute("ALTER TABLE nds_v31_intake_pending ADD CONSTRAINT ck_pending_state "
               "CHECK (state IN ('pending', 'retry', 'processing', 'acknowledged'))")
    op.execute('ALTER TABLE nds_v31_intake_pending ADD CONSTRAINT ck_pending_attempts CHECK (attempts >= 0)')
    op.execute("ALTER TABLE nds_v31_intake_pending ADD CONSTRAINT ck_pending_claim "
               "CHECK (state NOT IN ('processing', 'acknowledged') OR "
               "(claim_token IS NOT NULL AND claim_actor IS NOT NULL AND lease_until IS NOT NULL))")
    op.execute('CREATE INDEX ix_pending_ready ON nds_v31_intake_pending (state, next_attempt_at, lease_until)')
    op.execute('CREATE INDEX ix_intake_scope ON nds_v31_intake_raw (project, destination, received_at, revision)')


def downgrade():
    raise PermissionError("Storage integrity changes require a reviewed forward repair")
