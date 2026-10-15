"""Executed PostgreSQL storage checks with synthetic data and injected policies.

Database integrity/roles are real. Injected service/NDS decisions are not live
permission evidence. No REDCap or backend request is made.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier
from types import SimpleNamespace
import importlib.util
from pathlib import Path

import pytest
from sqlalchemy import inspect, select, func, text, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from etl.config import Settings
from etl.load.db import create_db_engine
from etl.intake.v31 import Intake, RecordIdentity, QueueConflict, IntakeUnavailable, raw, head, pending, audit
from etl.repository.v31 import Repository, RegistryDecision, RecordIdentity as ResearchIdentity, raw as research_raw
from etl.repository.participant_links import ParticipantLinks

SCHEMA = 'neps_source'
POLICY = SimpleNamespace(authorises=lambda scope: True)


def store(engine, project='synthetic-project', destination='synthetic-store', clock=None):
    args = {} if clock is None else {'clock': clock}
    return Intake(engine, project=project, destination=destination,
                  service_identity='synthetic-collector', policy=POLICY, **args)


def count(engine, table):
    with engine.connect() as c:
        return c.execute(select(func.count()).select_from(table)).scalar_one()


def test_fresh_upgrade_and_frozen_schema_matches_definitions(pg_database):
    db = pg_database
    db['migrate']('002_independent_source_intake')
    with db['owner'].connect() as c:
        from etl.intake.v31 import metadata as intake
        from etl.repository.v31 import metadata as research
        from etl.repository.participant_links import metadata as links
        inspector = inspect(c)
        for table in [*intake.tables.values(), *research.tables.values(), *links.tables.values()]:
            actual = {col['name']: col for col in inspector.get_columns(table.name, schema=SCHEMA)}
            assert set(actual) == {col.name for col in table.columns}
            assert inspector.get_pk_constraint(table.name, schema=SCHEMA)['constrained_columns'] == [c.name for c in table.primary_key]
            for col in table.columns:
                assert actual[col.name]['nullable'] == col.nullable
                expected_type = str(col.type.compile(dialect=c.dialect))
                actual_type = str(actual[col.name]['type'].compile(dialect=c.dialect))
                assert actual_type == expected_type or {actual_type, expected_type} <= {'FLOAT', 'DOUBLE PRECISION'}
        assert not any(name.startswith('nds_v31_') for name in inspector.get_table_names(schema='public'))
    db['migrate']()
    with db['owner'].connect() as c:
        assert c.exec_driver_sql(f'SELECT version_num FROM {SCHEMA}.alembic_version').scalar_one() == '004_storage_integrity'
        inspector = inspect(c)
        for table in [*intake.tables.values(), *research.tables.values(), *links.tables.values()]:
            expected_unique = {tuple(col.name for col in constraint.columns)
                               for constraint in table.constraints
                               if constraint.__class__.__name__ == 'UniqueConstraint'}
            actual_unique = {tuple(item['column_names']) for item in inspector.get_unique_constraints(table.name, schema=SCHEMA)}
            assert expected_unique == actual_unique
            expected_foreign = {(tuple(col.name for col in constraint.columns),
                                 tuple(element.column.name for element in constraint.elements))
                                for constraint in table.foreign_key_constraints}
            actual_foreign = {(tuple(item['constrained_columns']),tuple(item['referred_columns']))
                              for item in inspector.get_foreign_keys(table.name, schema=SCHEMA)}
            assert expected_foreign == actual_foreign



def test_upgrade_from_001_preserves_rows_and_adds_all_eleven_columns(pg_database):
    db = pg_database
    db['migrate']('001_initial')
    with db['owner'].begin() as c:
        c.exec_driver_sql("INSERT INTO redcap.raw_redcap_demographics (record_id,redcap_event_name,age) VALUES ('synthetic-legacy','baseline',17)")
        c.exec_driver_sql("INSERT INTO redcap.raw_redcap_monthly_self_report (record_id,redcap_event_name,anxiety_score) VALUES ('synthetic-legacy','baseline',2.5)")
    db['migrate']()
    with db['owner'].connect() as c:
        demo = c.exec_driver_sql('SELECT * FROM redcap.raw_redcap_demographics').mappings().one()
        monthly = c.exec_driver_sql('SELECT * FROM redcap.raw_redcap_monthly_self_report').mappings().one()
        assert demo['record_id'] == 'synthetic-legacy' and demo['age'] == 17
        assert monthly['anxiety_score'] == 2.5
        for key in ['employment_status', 'food_security', 'healthcare_access', 'socioeconomic_status']:
            assert demo[key] is None
        for key in ['mood_score', 'sleep_quality_score', 'fatigue_score', 'attendance_score', 'coping_score', 'substance_abuse_score', 'suicidality_score']:
            assert monthly[key] is None
    db['migrate']()  # Already at head, no rewrite or duplicate columns.


def test_concurrent_receipt_replay_and_amendments_are_durable(pg_database):
    db = pg_database; db['migrate'](); db['grants']()
    engine = db['engine']('de03_collector')
    barrier = Barrier(8)
    identity = RecordIdentity('synthetic-project', 'same-source')
    def receive(n):
        barrier.wait()
        return store(engine).receive(identity, {'study_id': 'same-source', 'answer': ''}, 'v1', 'fixture')
    with ThreadPoolExecutor(max_workers=8) as pool:
        ids = list(pool.map(receive, range(8)))
    assert len(set(ids)) == 1
    assert count(engine, raw) == count(engine, head) == count(engine, audit) == 1
    barrier = Barrier(8)
    def amend(n):
        barrier.wait()
        return store(engine).receive(identity, {'study_id': 'same-source', 'answer': str(n)}, 'v1', 'fixture')
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert len(set(pool.map(amend, range(8)))) == 8
    with engine.connect() as c:
        rows = c.execute(select(raw).order_by(raw.c.revision)).mappings().all()
        assert [r['revision'] for r in rows] == list(range(1,10))
        assert {r['payload']['answer'] for r in rows} == {'', *map(str, range(8))}


def test_concurrent_claim_expiry_stale_ack_retry_and_requeue(pg_database):
    db = pg_database; db['migrate'](); db['grants']()
    collector = store(db['engine']('de03_collector'))
    clock = [1000.0]
    worker = store(db['engine']('de03_worker'), clock=lambda: clock[0])
    for n in range(8):
        collector.receive(RecordIdentity('synthetic-project', str(n)), {'study_id': str(n)}, 'v1', 'fixture')
    # Receipt time is real, queue readiness is real. Set test clock after it.
    import time
    clock[0] = time.time() + 1
    barrier = Barrier(8)
    def claim(n):
        barrier.wait()
        return worker.claim('worker-' + str(n), lease_seconds=10)
    with ThreadPoolExecutor(max_workers=8) as pool:
        claims = list(pool.map(claim, range(8)))
    assert all(claims) and len({c.source_revision_id for c in claims}) == 8
    assert worker.claim('extra') is None
    clock[0] += 11
    recovered = worker.claim('recovery', lease_seconds=10)
    original = next(c for c in claims if c.source_revision_id == recovered.source_revision_id)
    assert recovered.attempts == 2 and recovered.claim_token != original.claim_token
    with pytest.raises(QueueConflict):
        worker.ack(original.source_revision_id, original.claim_token, 'worker-' + str(claims.index(original)))
    worker.fail(recovered.source_revision_id, recovered.claim_token, 'recovery', 'nds_unavailable')
    retry = worker.claim('retry')
    assert retry.source_revision_id == recovered.source_revision_id
    worker.ack(retry.source_revision_id, retry.claim_token, 'retry')
    worker.ack(retry.source_revision_id, retry.claim_token, 'retry')
    worker.requeue(retry.source_revision_id, 'reviewed-requeue')
    again = worker.claim('again')
    assert again.source_revision_id == retry.source_revision_id
    with pytest.raises(QueueConflict):
        worker.requeue(again.source_revision_id, 'cannot-steal')
    assert count(db['engine'](), raw) == 8


def test_interrupted_receipt_rolls_back_all_layers(pg_database, monkeypatch):
    db = pg_database; db['migrate']()
    engine = db['engine'](); intake = store(engine)
    def interrupt(*args):
        raise RuntimeError('synthetic interruption before commit')
    monkeypatch.setattr(intake, '_audit', interrupt)
    with pytest.raises(RuntimeError):
        intake.receive(RecordIdentity('synthetic-project', 'interrupted'), {'study_id': 'interrupted'}, 'v1', 'fixture')
    for table in [raw, head, pending, audit]:
        assert count(engine, table) == 0
    with engine.connect() as c:
        tx = c.begin()
        c.execute(text(f"INSERT INTO {SCHEMA}.nds_v31_participant_links VALUES ('p','s','nds-s','v1')"))
        tx.rollback()
    with engine.connect() as c:
        assert c.exec_driver_sql(f'SELECT count(*) FROM {SCHEMA}.nds_v31_participant_links').scalar_one() == 0


def test_scope_constraints_and_append_only_roles(pg_database):
    db = pg_database; db['migrate'](); db['grants']()
    collector_engine = db['engine']('de03_collector')
    ids = []
    for project,destination in [('p1','a'),('p1','b'),('p2','a')]:
        ids.append(store(collector_engine,project,destination).receive(RecordIdentity(project,'same'),{'study_id':'same'},'v1','fixture'))
    assert len(set(ids)) == 3 and count(collector_engine,raw) == 3
    with collector_engine.connect() as c:
        rows = c.execute(select(raw)).mappings().all()
        first,second = rows[:2]
    with pytest.raises(IntegrityError), db['engine']().begin() as c:
        c.execute(update(head).where(head.c.identity_key==first['identity_key']).values(source_revision_id=second['id']))
    for role in ['de03_collector','de03_worker','de03_processor','de03_links','de03_reviewer']:
        e=db['engine'](role)
        with e.connect() as c:
            assert c.exec_driver_sql("SELECT NOT rolsuper AND NOT rolbypassrls AND NOT pg_has_role(current_user,'de03_owner','USAGE') FROM pg_roles WHERE rolname=current_user").scalar_one()
        for table in ['nds_v31_intake_raw','nds_v31_intake_audit','nds_v31_source','nds_v31_audit']:
            for operation in ['UPDATE','DELETE','TRUNCATE']:
                with e.connect() as c:
                    assert c.execute(text('SELECT has_table_privilege(current_user,:t,:p)'),{'t':SCHEMA+'.'+table,'p':operation}).scalar_one() is False
        with pytest.raises(DBAPIError), e.begin() as c:
            c.exec_driver_sql(f'TRUNCATE {SCHEMA}.nds_v31_intake_raw CASCADE')
    with pytest.raises(DBAPIError), collector_engine.begin() as c:
        c.exec_driver_sql(f"UPDATE {SCHEMA}.nds_v31_intake_raw SET source_version='tampered'")
    with pytest.raises(DBAPIError), collector_engine.begin() as c:
        c.exec_driver_sql(f'DELETE FROM {SCHEMA}.nds_v31_intake_audit')
    assert count(collector_engine,raw) == count(collector_engine,audit) == 3


class ResearchPolicy:
    def resolve(self, identity): return RegistryDecision('Ghana',True,True,'NDS-synthetic')
    def permits(self,*args): return True
    def transfer_permitted(self,*args): return True


def test_research_destination_and_concurrent_results(pg_database):
    db=pg_database;db['migrate']();db['grants']()
    engine=db['engine']('de03_processor')
    identity=ResearchIdentity('p','same','','','')
    a=Repository(engine,ResearchPolicy(),storage_destination='a')
    b=Repository(engine,ResearchPolicy(),storage_destination='b')
    barrier=Barrier(8)
    def ingest(n):
        barrier.wait()
        return a.ingest(identity,{'study_id':'same','k6_1':''},'v1','fixture')
    with ThreadPoolExecutor(max_workers=8) as pool:
        ids=list(pool.map(ingest,range(8)))
    assert len(set(ids))==1
    other=b.ingest(identity,{'study_id':'same','k6_1':'4'},'v1','fixture')
    assert other!=ids[0]
    assert a.export(identity,'fixture','permitted-export')['payload']['k6_1']==''
    assert b.export(identity,'fixture','permitted-export')['payload']['k6_1']=='4'
    with pytest.raises(PermissionError):b.store_derived(ids[0],'calc-v1',{},'fixture')
    barrier=Barrier(8)
    def derive(n):
        barrier.wait()
        return a.store_derived(ids[0],'calc-v1',{'synthetic':'result'},'fixture')
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert len(set(pool.map(derive,range(8))))==1
    assert count(engine,research_raw)==2


def test_concurrent_verified_link_binding_is_idempotent(pg_database):
    db=pg_database;db['migrate']();db['grants']()
    links=ParticipantLinks(db['engine']('de03_links'),authoriser=lambda *args:True)
    barrier=Barrier(8)
    def bind(n):
        barrier.wait()
        return links.bind('p','source','NDS-source','v1','synthetic-authority')
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert all(x['nds_id']=='NDS-source' for x in pool.map(bind,range(8)))
    with pytest.raises(ValueError):links.bind('p','source','NDS-changed','v2','synthetic-authority')


def test_upgrade_from_002_preserves_all_existing_source_rows(pg_database):
    from etl.repository.integrity import storage_snapshot
    db=pg_database;db['migrate']('002_independent_source_intake')
    engine=db['engine']();intake=store(engine)
    i=RecordIdentity('synthetic-project','retained')
    intake.receive(i,{'study_id':'retained','answer':''},'v1','fixture')
    intake.receive(i,{'study_id':'retained','answer':'corrected'},'v1','fixture')
    before=storage_snapshot(engine,SCHEMA)
    db['migrate']()
    assert storage_snapshot(engine,SCHEMA)==before


def test_incompatible_manual_column_repair_fails_without_data_loss(pg_database):
    db=pg_database;db['migrate']('002_independent_source_intake')
    with db['owner'].begin() as c:
        c.exec_driver_sql('ALTER TABLE redcap.raw_redcap_monthly_self_report ADD COLUMN mood_score TEXT')
        c.exec_driver_sql("INSERT INTO redcap.raw_redcap_monthly_self_report (record_id,redcap_event_name,mood_score) VALUES ('synthetic','baseline','preserve-verbatim')")
    with pytest.raises(DBAPIError):db['migrate']()
    with db['owner'].connect() as c:
        assert c.exec_driver_sql('SELECT mood_score FROM redcap.raw_redcap_monthly_self_report').scalar_one()=='preserve-verbatim'
        assert c.exec_driver_sql(f'SELECT version_num FROM {SCHEMA}.alembic_version').scalar_one()=='002_independent_source_intake'


def test_server_interrupted_transaction_rolls_back_and_retries(pg_database,pg_admin,monkeypatch):
    db=pg_database;db['migrate']();engine=db['engine']();intake=store(engine)
    original=intake._audit
    def disconnect(connection,*args):
        pid=connection.exec_driver_sql('SELECT pg_backend_pid()').scalar_one()
        with pg_admin.connect() as admin:
            assert admin.execute(text('SELECT pg_terminate_backend(:pid)'),{'pid':pid}).scalar_one()
        connection.exec_driver_sql('SELECT 1')
    monkeypatch.setattr(intake,'_audit',disconnect)
    identity=RecordIdentity('synthetic-project','server-interrupted')
    with pytest.raises(IntakeUnavailable):intake.receive(identity,{'study_id':'server-interrupted'},'v1','fixture')
    for table in [raw,head,pending,audit]:assert count(engine,table)==0
    monkeypatch.setattr(intake,'_audit',original)
    intake.receive(identity,{'study_id':'server-interrupted'},'v1','fixture')
    for table in [raw,head,pending,audit]:assert count(engine,table)==1


def test_runtime_engine_targets_explicit_schema(pg_database):
    db=pg_database;db['migrate']();db['grants']()
    settings=Settings(_env_file=None,DATABASE_URL=db['url'].set(username='de03_collector').render_as_string(hide_password=False),WAREHOUSE_SCHEMA=SCHEMA)
    engine=create_db_engine(settings)
    try:
        intake=store(engine)
        intake.receive(RecordIdentity('synthetic-project','runtime'),{'study_id':'runtime'},'v1','fixture')
        assert count(engine,raw)==1
        assert engine.hide_parameters is True
    finally:engine.dispose()


def test_invalid_existing_head_blocks_upgrade_without_rewriting_history(pg_database):
    from etl.repository.integrity import storage_snapshot
    db=pg_database;db['migrate']('002_independent_source_intake')
    engine=db['engine']();intake=store(engine)
    for key in ['one','two']:
        intake.receive(RecordIdentity('synthetic-project',key),{'study_id':key},'v1','fixture')
    with engine.begin() as c:
        rows=c.execute(select(raw)).mappings().all()
        c.execute(update(head).where(head.c.identity_key==rows[0]['identity_key']).values(source_revision_id=rows[1]['id']))
    before=storage_snapshot(engine,SCHEMA)
    with pytest.raises(IntegrityError):db['migrate']()
    assert storage_snapshot(engine,SCHEMA)==before
    with db['owner'].connect() as c:
        assert c.exec_driver_sql(f'SELECT version_num FROM {SCHEMA}.alembic_version').scalar_one()=='002_independent_source_intake'


def test_readonly_snapshot_cli_preserves_existing_evidence(pg_database,tmp_path):
    import json,os,subprocess,sys
    db=pg_database;db['migrate']()
    intake=store(db['engine']())
    intake.receive(RecordIdentity('synthetic-project','snapshot'),{'study_id':'snapshot'},'v1','fixture')
    url_file=tmp_path/'url'
    url_file.write_text(db['url'].set(username='de03_owner').render_as_string(hide_password=False))
    output=tmp_path/'snapshot.json'
    command=[sys.executable,'-m','ops.storage_snapshot','--url-file',str(url_file),'--schema',SCHEMA,'--output',str(output)]
    env={'PATH':os.environ['PATH'],'LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1',
         'REDCAP_API_TOKEN_FILE':'/synthetic-nonexistent-secret-must-not-be-read'}
    result=subprocess.run(command,cwd=Path(__file__).parents[2],env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    before=output.read_bytes()
    assert json.loads(before)['nds_v31_intake_raw']['count']==1
    result=subprocess.run(command,cwd=Path(__file__).parents[2],env=env,capture_output=True,text=True)
    assert result.returncode!=0 and output.read_bytes()==before
