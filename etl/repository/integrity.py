"""Count and digest retained storage for an explicitly authorised recovery check.

No payloads are printed or returned. Run during the DBA's quiesced backup window
or compare the same database snapshot. A digest is not an access permission.
"""
import hashlib
import json

from sqlalchemy import MetaData, Table, select, text
from etl.config import validate_warehouse_schema

TABLES = [
    'nds_v31_intake_raw', 'nds_v31_intake_head', 'nds_v31_intake_pending',
    'nds_v31_intake_audit', 'nds_v31_participant_links', 'nds_v31_source',
    'nds_v31_validated', 'nds_v31_derived', 'nds_v31_audit',
]


def storage_snapshot(engine, schema):
    validate_warehouse_schema(schema)
    if not schema or engine.dialect.name != 'postgresql':
        raise ValueError('Explicit PostgreSQL schema required')
    result = {}
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as c:
        with c.begin():
            c.exec_driver_sql('SET TRANSACTION READ ONLY')
            for name in TABLES:
                table = Table(name, MetaData(), schema=schema, autoload_with=c)
                digest = hashlib.sha256()
                count = 0
                for row in c.execute(select(table).order_by(*table.primary_key.columns)).mappings():
                    value = json.dumps(dict(row), sort_keys=True, separators=(',', ':'),
                                       ensure_ascii=False, allow_nan=False)
                    digest.update(value.encode()); digest.update(b'\n'); count += 1
                result[name] = {'count': count, 'sha256': digest.hexdigest()}
    return result
