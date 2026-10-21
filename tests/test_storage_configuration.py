"""Configuration and offline rendering. These are not database execution tests."""
from io import StringIO
from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest

from etl.config import Settings
from etl.load.db import create_db_engine, database_url


@pytest.mark.parametrize('schema',['', 'pg_catalog','pg_private','information_schema','bad-name','a,b','x; DROP TABLE t','AUpper','a'*64])
def test_schema_rejects_ambiguous_or_reserved_names(schema):
    with pytest.raises(ValueError):Settings(_env_file=None,WAREHOUSE_SCHEMA=schema)


def test_postgresql_requires_explicit_schema_before_connection():
    with pytest.raises(ValueError,match='WAREHOUSE_SCHEMA'):
        create_db_engine(Settings(_env_file=None))


def test_bare_postgresql_url_uses_declared_driver():
    assert database_url('postgresql://synthetic@localhost/synthetic').drivername=='postgresql+psycopg2'
    assert database_url('sqlite:///:memory:').drivername=='sqlite'


def test_offline_upgrade_renders_explicit_schema_and_additive_repairs():
    root=Path(__file__).parents[1]
    output=StringIO();config=Config(str(root/'alembic.ini'),output_buffer=output)
    config.set_main_option('script_location',str(root/'alembic'))
    config.attributes['warehouse_schema']='synthetic_review'
    config.attributes['database_url']='postgresql://synthetic@localhost/synthetic'
    command.upgrade(config,'001_initial:head',sql=True)
    sql=output.getvalue()
    assert 'SET LOCAL search_path TO synthetic_review, pg_catalog' in sql
    assert 'CREATE TABLE nds_v31_intake_raw' in sql
    assert 'ADD COLUMN IF NOT EXISTS mood_score DOUBLE PRECISION' in sql
    assert 'UNIQUE (identity_key, storage_destination, revision)' in sql
    assert 'DROP SCHEMA' not in sql and 'DROP TABLE' not in sql
