"""Additive V3.1 intake/link/research tables; immutable DDL snapshot.

No registry or consent migration. Applying to a real database is a separate
release step; existing records/tables are not rewritten. Nonempty tables block
rollback; source retention/recovery requires explicit later authorisation.
"""
from alembic import op, context
from sqlalchemy import text
revision = "002_independent_source_intake"
down_revision = "001_initial"
branch_labels = None
depends_on = None
DDL = ['CREATE TABLE nds_v31_intake_raw (\n\tid VARCHAR NOT NULL, \n\tproject VARCHAR NOT NULL, \n\tidentity_key VARCHAR NOT NULL, \n\tidentity JSON NOT NULL, \n\trevision INTEGER NOT NULL, \n\tpayload JSON NOT NULL, \n\tpayload_hash VARCHAR NOT NULL, \n\tsource_version VARCHAR NOT NULL, \n\trecord_id_field VARCHAR NOT NULL, \n\tmetadata_snapshot JSON, \n\tmetadata_hash VARCHAR, \n\tcontract_hash VARCHAR NOT NULL, \n\treceived_at FLOAT NOT NULL, \n\tdestination VARCHAR NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (identity_key, revision)\n)', 'CREATE TABLE nds_v31_intake_audit (\n\tid VARCHAR NOT NULL, \n\tsource_revision_id VARCHAR NOT NULL, \n\taction VARCHAR NOT NULL, \n\tactor VARCHAR NOT NULL, \n\tat FLOAT NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(source_revision_id) REFERENCES nds_v31_intake_raw (id)\n)', 'CREATE TABLE nds_v31_intake_head (\n\tidentity_key VARCHAR NOT NULL, \n\trevision INTEGER NOT NULL, \n\tsource_revision_id VARCHAR NOT NULL, \n\tPRIMARY KEY (identity_key), \n\tFOREIGN KEY(source_revision_id) REFERENCES nds_v31_intake_raw (id)\n)', 'CREATE TABLE nds_v31_intake_pending (\n\tsource_revision_id VARCHAR NOT NULL, \n\tstate VARCHAR NOT NULL, \n\tattempts INTEGER NOT NULL, \n\tfailure_code VARCHAR, \n\tnext_attempt_at FLOAT NOT NULL, \n\tclaim_token VARCHAR, \n\tclaim_actor VARCHAR, \n\tlease_until FLOAT, \n\tPRIMARY KEY (source_revision_id), \n\tFOREIGN KEY(source_revision_id) REFERENCES nds_v31_intake_raw (id)\n)', 'CREATE TABLE nds_v31_participant_links (\n\tproject VARCHAR NOT NULL, \n\tsource_id VARCHAR NOT NULL, \n\tnds_id VARCHAR NOT NULL, \n\tmapping_version VARCHAR NOT NULL, \n\tPRIMARY KEY (project, source_id)\n)', 'CREATE TABLE nds_v31_source (\n\tid VARCHAR NOT NULL, \n\tidentity_key VARCHAR NOT NULL, \n\tidentity JSON NOT NULL, \n\trevision INTEGER NOT NULL, \n\tchange_hash VARCHAR NOT NULL, \n\tsource_version VARCHAR NOT NULL, \n\tcontract_version VARCHAR NOT NULL, \n\tpayload JSON NOT NULL, \n\tcountry VARCHAR NOT NULL, \n\tobserved_at VARCHAR NOT NULL, \n\tcontract_hash VARCHAR NOT NULL, \n\tstorage_destination VARCHAR NOT NULL, \n\tnds_participant_id VARCHAR, \n\tintake_revision_id VARCHAR, \n\tsource_metadata_hash VARCHAR, \n\tsource_metadata JSON, \n\tPRIMARY KEY (id), \n\tUNIQUE (identity_key, revision)\n)', 'CREATE TABLE nds_v31_audit (\n\tid VARCHAR NOT NULL, \n\tsource_id VARCHAR NOT NULL, \n\taction VARCHAR NOT NULL, \n\tactor VARCHAR NOT NULL, \n\tat VARCHAR NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(source_id) REFERENCES nds_v31_source (id)\n)', 'CREATE TABLE nds_v31_derived (\n\tid VARCHAR NOT NULL, \n\tsource_id VARCHAR NOT NULL, \n\tcalculation_version VARCHAR NOT NULL, \n\tresult JSON NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (source_id, calculation_version), \n\tFOREIGN KEY(source_id) REFERENCES nds_v31_source (id)\n)', 'CREATE TABLE nds_v31_validated (\n\tsource_id VARCHAR NOT NULL, \n\t"values" JSON NOT NULL, \n\tissues JSON NOT NULL, \n\tPRIMARY KEY (source_id), \n\tFOREIGN KEY(source_id) REFERENCES nds_v31_source (id)\n)']
TABLES = ['nds_v31_intake_raw', 'nds_v31_intake_audit', 'nds_v31_intake_head', 'nds_v31_intake_pending', 'nds_v31_participant_links', 'nds_v31_source', 'nds_v31_audit', 'nds_v31_derived', 'nds_v31_validated']

def upgrade():
    for statement in DDL:
        op.execute(statement)

def downgrade():
    if context.is_offline_mode():
        raise PermissionError("Offline destructive rollback is not authorised")
    connection = op.get_bind()
    for name in TABLES:
        if connection.execute(text('SELECT COUNT(*) FROM ' + name)).scalar_one():
            raise PermissionError("Retained source/link/research data prevent destructive rollback")
    for name in reversed(TABLES):
        op.drop_table(name)
