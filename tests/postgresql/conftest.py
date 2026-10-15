"""Explicitly opted-in PostgreSQL tests. Never fall back to SQLite."""
import os
import json
import subprocess
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, text
from etl.load.db import database_url

SCHEMA = 'neps_source'


@pytest.fixture(scope='session')
def pg_admin():
    ref = os.environ.get('NEPS_DE03_PG_URL_FILE')
    if not ref:
        pytest.skip('Requires approved synthetic PostgreSQL and NEPS_DE03_PG_URL_FILE')
    if os.environ.get('NEPS_DE03_APPROVED') != 'synthetic-disposable':
        pytest.fail('Explicit synthetic disposable scope approval is required')
    url = database_url(Path(ref).read_text().strip())
    if url.get_backend_name() != 'postgresql':
        pytest.fail('PostgreSQL is required, no substitute database accepted')
    container = os.environ.get('NEPS_DE03_CONTAINER', '')
    if url.host != '127.0.0.1' or url.database != 'neps_de03_seed' or not container.startswith('neps-de03-synthetic-'):
        pytest.fail('This administrative fixture is restricted to the new local DE03 container')
    label = subprocess.check_output(['docker', 'inspect', '--format', '{{index .Config.Labels "neps.task"}}', container], text=True).strip()
    ports = json.loads(subprocess.check_output(['docker', 'inspect', '--format', '{{json .NetworkSettings.Ports}}', container], text=True))
    if label != 'DE03' or not any(p['HostIp'] == '127.0.0.1' and int(p['HostPort']) == url.port for p in ports['5432/tcp']):
        pytest.fail('URL does not identify the labelled disposable fixture')

    engine = create_engine(url, isolation_level='AUTOCOMMIT', hide_parameters=True, echo=False)
    with engine.connect() as c:
        assert c.dialect.name == 'postgresql'
        assert c.execute(text('SHOW server_version_num')).scalar_one().startswith('18')
        for name in ['de03_owner', 'de03_collector', 'de03_worker', 'de03_processor', 'de03_links', 'de03_reviewer']:
            if not c.execute(text('SELECT 1 FROM pg_roles WHERE rolname=:r'), {'r': name}).scalar():
                c.exec_driver_sql(f'CREATE ROLE {name} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS')
    yield engine
    engine.dispose()


@pytest.fixture
def pg_database(pg_admin):
    name = 'neps_de03_' + uuid4().hex[:16]
    with pg_admin.connect() as c:
        c.exec_driver_sql(f'CREATE DATABASE {name} OWNER de03_owner')
    url = pg_admin.url.set(database=name)
    owner = create_engine(url.set(username='de03_owner'), hide_parameters=True, echo=False)
    with owner.begin() as c:
        c.exec_driver_sql(f'CREATE SCHEMA {SCHEMA} AUTHORIZATION de03_owner')
    engines = []

    def engine(role='de03_owner'):
        e = create_engine(url.set(username=role), hide_parameters=True, echo=False,
                          execution_options={'schema_translate_map': {None: SCHEMA}})
        engines.append(e)
        return e

    def migrate(revision='head'):
        config = Config(str(Path(__file__).parents[2] / 'alembic.ini'))
        config.set_main_option('script_location', str(Path(__file__).parents[2] / 'alembic'))
        config.attributes['warehouse_schema'] = SCHEMA
        with owner.begin() as c:
            config.attributes['connection'] = c
            command.upgrade(config, revision)

    def grants():
        sql = (Path(__file__).parents[2] / 'ops/de03_role_grants.sql').read_text()
        for variable, value in {'schema': SCHEMA, 'collector': 'de03_collector', 'worker': 'de03_worker',
                                'processor': 'de03_processor', 'links': 'de03_links', 'reviewer': 'de03_reviewer'}.items():
            sql = sql.replace(':"' + variable + '"', '"' + value + '"')
        with owner.begin() as c:
            c.exec_driver_sql(sql)
            c.exec_driver_sql(f'REVOKE CREATE ON SCHEMA {SCHEMA} FROM PUBLIC')

    yield {'owner': owner, 'engine': engine, 'migrate': migrate, 'grants': grants, 'url': url, 'name': name}
    for e in engines:
        e.dispose()
    owner.dispose()
    with pg_admin.connect() as c:
        # Drop only this fixture's generated disposable database.
        c.exec_driver_sql(f'DROP DATABASE {name} WITH (FORCE)')
