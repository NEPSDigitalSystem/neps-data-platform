"""Static SQL preparation and fixture opt-in checks. No database execution."""
import os
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql

from etl.analytics.query_library import QUERIES, prepare_query, run_query


def scope():
    return dict(project='SYNTHETIC-PROJECT', destination='synthetic-store',
                field='age_years', algorithm_version='SYNTHETIC-ALGORITHM',
                metadata_policy_version='synthetic-policy', expected_contract_version='synthetic-v1',
                expected_contract_hash='synthetic-hash', dataset_class='synthetic')


@pytest.mark.parametrize('name', QUERIES)
def test_each_reviewed_statement_compiles_with_bound_scope(name):
    statement, params = prepare_query(name, 'synthetic_source', **scope())
    compiled = statement.compile(dialect=postgresql.dialect())
    assert set(compiled.params) <= set(params)
    assert '__WAREHOUSE_SCHEMA__' not in str(compiled)
    assert 'synthetic_source.nds_v31_source' in str(compiled)
    assert 'SYNTHETIC-PROJECT' not in str(compiled)
    assert ':project' in str(statement) and ':destination' in str(statement)


def test_schema_is_quoted_and_values_cannot_become_sql():
    injected = "x' OR true --"
    statement, params = prepare_query('null_analysis', 'select', **(scope() | {'field': injected, 'project': injected}))
    assert '"select".nds_v31_source' in str(statement)
    assert injected not in str(statement)
    assert params['project'] == params['field'] == injected
    with pytest.raises(ValueError):
        prepare_query('data_counts', 'x; DROP TABLE records', **scope())
    with pytest.raises(ValueError):
        prepare_query('../other', 'synthetic_source', **scope())


@pytest.mark.parametrize('change', [{'project': ''}, {'destination': None}, {'sample_limit': True},
                                  {'sample_limit': 0}, {'sample_limit': 21}, {'country': 1}])
def test_invalid_scope_is_rejected_before_any_connection(change):
    with pytest.raises(ValueError):
        prepare_query('data_counts', 'synthetic_source', **(scope() | change))


def test_sample_requires_explicit_approved_dataset_class():
    with pytest.raises(PermissionError):
        prepare_query('sample_records', 'synthetic_source', **(scope() | {'dataset_class': None}))
    with pytest.raises(ValueError):
        run_query(create_engine('sqlite:///:memory:'), 'data_counts', 'synthetic_source', **scope())


@pytest.mark.parametrize('mode', ['incomplete', 'unapproved', 'wrong_backend'])
def test_bad_postgresql_opt_in_fails_instead_of_skipping(tmp_path, mode):
    env = dict(PATH=os.environ['PATH'], LANG='C.UTF-8', PYTHONDONTWRITEBYTECODE='1',
               PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    if mode == 'incomplete':
        env['NEPS_DE03_APPROVED'] = 'synthetic-disposable'
        message = 'Incomplete synthetic PostgreSQL opt-in'
    else:
        url = tmp_path/'url';url.write_text('sqlite:///:memory:')
        env['NEPS_DE03_PG_URL_FILE'] = str(url)
        if mode == 'wrong_backend':
            env['NEPS_DE03_APPROVED'] = 'synthetic-disposable'
            message = 'PostgreSQL is required'
        else:
            message = 'Explicit synthetic disposable scope approval is required'
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/postgresql/test_reporting_queries.py',
                             '-q', '-k', 'empty_reporting_scope'],
                            cwd=Path(__file__).parents[1], env=env, capture_output=True, text=True)
    assert result.returncode == 1
    assert message in result.stdout
    assert 'skipped' not in result.stdout
