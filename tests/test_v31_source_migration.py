"""Candidate frozen DDL executed only on disposable SQLite, never PostgreSQL."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import pytest
from sqlalchemy import create_engine,inspect,text,event
from etl.intake.v31 import Intake,RecordIdentity


def revision():
    p=Path(__file__).parents[1]/'alembic/versions/002_independent_source_intake.py'
    spec=importlib.util.spec_from_file_location('source_migration',p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def bind(m,c):
    m.op=SimpleNamespace(execute=lambda sql:c.exec_driver_sql(sql),get_bind=lambda:c,
                         drop_table=lambda name:c.exec_driver_sql('DROP TABLE '+name))
    m.context=SimpleNamespace(is_offline_mode=lambda:False)


def test_candidate_empty_upgrade_and_guarded_rollback():
    e=create_engine('sqlite:///:memory:');m=revision()
    with e.begin() as c:
        bind(m,c);m.upgrade()
        assert set(inspect(c).get_table_names())==set(m.TABLES)
        m.downgrade();assert inspect(c).get_table_names()==[]
        m.upgrade();assert len(inspect(c).get_table_names())==9


def test_received_data_block_destructive_rollback():
    e=create_engine('sqlite:///:memory:');m=revision()
    @event.listens_for(e,'connect')
    def fk(c,r):c.execute('PRAGMA foreign_keys=ON')
    with e.begin() as c:bind(m,c);m.upgrade()
    p=SimpleNamespace(authorises=lambda scope:True)
    intake=Intake(e,project='synthetic-project',destination='synthetic-store',service_identity='synthetic-service',policy=p)
    intake.receive(RecordIdentity('synthetic-project','0001'),{'study_id':'0001'},'synthetic-v1','fixture')
    with e.begin() as c:
        bind(m,c)
        with pytest.raises(PermissionError,match='Retained'):m.downgrade()
        assert set(inspect(c).get_table_names())==set(m.TABLES)
        assert c.execute(text('SELECT COUNT(*) FROM nds_v31_intake_raw')).scalar_one()==1
