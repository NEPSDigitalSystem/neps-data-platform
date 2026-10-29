"""Reviewed PostgreSQL reports. Values are bound; schema names are validated.

Database read permission and an approved reporting scope are caller duties.
These reports do not query the NDS service or establish current consent.
"""
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.dialects import postgresql

from etl.config import validate_warehouse_schema

QUERIES = ('data_counts', 'scoring_distribution', 'null_analysis',
           'country_distribution', 'contract_version_check', 'sample_records')
QUERY_ROOT = Path(__file__).resolve().parents[2] / 'docs' / 'sql_queries'


def prepare_query(name, schema, *, project, destination, country=None, event=None,
                  instrument=None, instance=None, field=None, algorithm_version=None,
                  metadata_policy_version=None, expected_contract_version=None,
                  expected_contract_hash=None, sample_limit=5, dataset_class=None):
    if name not in QUERIES:
        raise ValueError('Choose a named reviewed query')
    if type(schema) is not str or not schema:
        raise ValueError('Explicit warehouse schema required')
    validate_warehouse_schema(schema)
    for value in (project, destination):
        if type(value) is not str or not value:
            raise ValueError('Explicit project and destination required')
    optional = (country, event, instrument, instance, field, algorithm_version,
                metadata_policy_version, expected_contract_version, expected_contract_hash)
    if any(value is not None and type(value) is not str for value in optional):
        raise ValueError('Optional scope values must be strings or None')
    if name == 'null_analysis' and not field:
        raise ValueError('Explicit field required')
    if name == 'scoring_distribution' and (not algorithm_version or not metadata_policy_version):
        raise ValueError('Explicit algorithm and metadata policy versions required')
    if name == 'contract_version_check' and (not expected_contract_version or not expected_contract_hash):
        raise ValueError('Explicit expected contract version and hash required')
    if type(sample_limit) is not int or not 1 <= sample_limit <= 20:
        raise ValueError('Sample limit must be between 1 and 20')
    if name == 'sample_records' and dataset_class not in ('synthetic', 'approved_deidentified'):
        raise PermissionError('Sample scope must be synthetic or approved de-identified')
    quoted = postgresql.dialect().identifier_preparer.quote_schema(schema)
    sql = (QUERY_ROOT / (name + '.sql')).read_text(encoding='utf-8')
    statement = text(sql.replace('__WAREHOUSE_SCHEMA__', quoted))
    params = dict(project=project, destination=destination, country=country,
                  event=event, instrument=instrument, instance=instance, field=field,
                  algorithm_version=algorithm_version, metadata_policy_version=metadata_policy_version,
                  expected_contract_version=expected_contract_version,
                  expected_contract_hash=expected_contract_hash, sample_limit=sample_limit,
                  dataset_class=dataset_class)
    return statement, params


def run_query(engine, name, schema, **scope):
    statement, params = prepare_query(name, schema, **scope)
    if engine.dialect.name != 'postgresql':
        raise ValueError('These reports require PostgreSQL')
    with engine.connect() as connection, connection.begin():
        connection.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY')
        connection.exec_driver_sql("SET LOCAL statement_timeout = '15s'")
        connection.exec_driver_sql("SET LOCAL lock_timeout = '3s'")
        return [dict(row) for row in connection.execute(statement, params).mappings()]
