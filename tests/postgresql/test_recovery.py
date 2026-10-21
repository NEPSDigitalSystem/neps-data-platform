"""Local synthetic pg_dump/pg_restore rehearsal, not DBA production acceptance."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

from etl.repository.integrity import storage_snapshot
from etl.repository.participant_links import ParticipantLinks
from etl.repository.v31 import Repository, RecordIdentity as ResearchIdentity
from test_storage import store, ResearchPolicy, SCHEMA
from etl.intake.v31 import RecordIdentity


def test_quiesced_dump_restore_matches_all_nine_tables(pg_database, pg_admin, tmp_path):
    container=os.environ.get('NEPS_DE03_CONTAINER')
    if not container:
        pytest.skip('Local Docker recovery rehearsal needs NEPS_DE03_CONTAINER; DBA procedure remains separate')
    # Restrict subprocess use to this task's isolated fixture.
    assert container.startswith('neps-de03-synthetic-')
    db=pg_database;db['migrate']();db['grants']();engine=db['engine']()
    clock=[time.time()]
    intake=store(engine,clock=lambda:clock[0]);identity=RecordIdentity('synthetic-project','backup-source')
    intake.receive(identity,{'study_id':'backup-source','answer':'','missing':None},'v1','fixture',metadata_snapshot=[{'field_name':'answer','meaning':'synthetic-v1'}])
    clock[0]+=1
    intake.receive(identity,{'study_id':'backup-source','answer':'corrected'},'v1','fixture',metadata_snapshot=[{'field_name':'answer','meaning':'synthetic-v2'}])
    claim=intake.claim('restore-worker',lease_seconds=10)
    intake.ack(claim.source_revision_id,claim.claim_token,'restore-worker')
    intake.receive(RecordIdentity('synthetic-project','backup-pending'),{'study_id':'backup-pending'},'v1','fixture')
    claim=intake.claim('crashed-worker',lease_seconds=10)
    links=ParticipantLinks(engine,authoriser=lambda *args:True)
    links.bind('synthetic-project','backup-source','NDS-backup-source','v1','fixture')
    repo=Repository(engine,ResearchPolicy(),storage_destination='synthetic-store')
    research_id=repo.ingest(ResearchIdentity('synthetic-project','backup-source','','',''),{'study_id':'backup-source','country':'1'},'v1','fixture')
    repo.store_derived(research_id,'synthetic-calculation-v1',{'provisional':True,'value':None},'fixture')
    before=storage_snapshot(engine,SCHEMA)
    assert all(row['count']>0 for row in before.values())
    destination='neps_de03_restore_'+uuid4().hex[:12]
    with pg_admin.connect() as admin:
        admin.exec_driver_sql(f'CREATE DATABASE {destination} OWNER de03_owner')
    restored=create_engine(db['url'].set(database=destination,username='de03_owner'),hide_parameters=True,echo=False,
                           execution_options={'schema_translate_map':{None:SCHEMA}})
    artifact=tmp_path/'synthetic.dump'
    commands=[]
    try:
        dump=['docker','exec',container,'pg_dump','-U','de03_owner','-d',db['name'],'--format=custom','--no-owner','--no-privileges']
        start=time.monotonic()
        with artifact.open('wb') as stream:
            p=subprocess.run(dump,stdout=stream,stderr=subprocess.PIPE,check=True)
        backup_seconds=time.monotonic()-start;commands.append(dump)
        restore=['docker','exec','-i',container,'pg_restore','-U','de03_owner','-d',destination,'--single-transaction','--exit-on-error','--no-owner','--no-privileges']
        start=time.monotonic()
        with artifact.open('rb') as stream:
            p=subprocess.run(restore,stdin=stream,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        restore_seconds=time.monotonic()-start;commands.append(restore)
        after=storage_snapshot(restored,SCHEMA)
        assert before==after
        with restored.connect() as c:
            assert c.exec_driver_sql(f'SELECT version_num FROM {SCHEMA}.alembic_version').scalar_one()=='004_storage_integrity'
            assert c.exec_driver_sql(f'SELECT count(*) FROM {SCHEMA}.nds_v31_intake_head h LEFT JOIN {SCHEMA}.nds_v31_intake_raw r ON r.id=h.source_revision_id AND r.identity_key=h.identity_key AND r.revision=h.revision WHERE r.id IS NULL').scalar_one()==0
        clock[0]+=11
        recovery=store(restored,clock=lambda:clock[0]).claim('new-worker')
        assert recovery.source_revision_id==claim.source_revision_id and recovery.claim_token!=claim.claim_token
        evidence={'scope':'local synthetic quiesced backup rehearsal','commands':commands,'before':before,'after':after,
                  'backup_seconds':backup_seconds,'restore_seconds':restore_seconds,
                  'dump_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),
                  'missing_committed_rows':0,'production_RPO_RTO_agreed':False,'DBA_acceptance':'pending'}
        output=os.environ.get('NEPS_DE03_RECOVERY_EVIDENCE')
        if output:Path(output).write_text(json.dumps(evidence,indent=2)+'\n')
    finally:
        restored.dispose()
        with pg_admin.connect() as admin:admin.exec_driver_sql(f'DROP DATABASE {destination} WITH (FORCE)')
