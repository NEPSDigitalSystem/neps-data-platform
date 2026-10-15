"""Independent intake durability and isolation tests; no NDS/live source data."""
import copy
import pytest
from sqlalchemy import create_engine,event,select,func
from etl.intake.v31 import Intake,RecordIdentity,IntakeDenied,QueueConflict,raw,head,pending,audit,metadata

class ServicePolicy:
 def __init__(self):self.grant=True;self.scopes=[]
 def authorises(self,scope):self.scopes.append(scope);return self.grant
 def resolve(self,*a):raise AssertionError('NDS registry must never gate intake')
 def permits(self,*a):raise AssertionError('NDS downstream consent must never gate intake')
@pytest.fixture
def store():
 e=create_engine('sqlite:///:memory:')
 @event.listens_for(e,'connect')
 def fk(c,r):c.execute('PRAGMA foreign_keys=ON')
 with e.begin() as c:metadata.create_all(c)
 clock=[1000.0];policy=ServicePolicy()
 r=Intake(e,project='source-project',destination='Ghana',service_identity='configured-service',policy=policy,clock=lambda:clock[0])
 i=RecordIdentity('source-project','SOURCE-ONLY-ID','baseline','','')
 p={'study_id':'SOURCE-ONLY-ID','redcap_event_name':'baseline','redcap_repeat_instrument':'','redcap_repeat_instance':''}
 return r,policy,i,p,clock

def count(r,t):
 with r.engine.connect() as c:return c.execute(select(func.count()).select_from(t)).scalar_one()

def test_intake_accepts_all_source_responses_and_separate_actual_consent_without_registry(store):
 r,policy,i,p,clock=store
 from pathlib import Path
 import json
 contract=json.loads((Path(__file__).parents[1]/'etl/contracts/data_contract_v31.json').read_text())
 payload=p|{name:['',None,'0'][n%3] for n,name in enumerate(contract['question_fields'])}
 # Arbitrary observed additional metadata is source-preserved, never interpreted as approved consent.
 payload['actual_source_field_from_metadata']='source-code'
 meta=[{'field_name':'actual_source_field_from_metadata','field_type':'radio'}]
 before=copy.deepcopy(payload)
 sid=r.receive(i,payload,'source-metadata-version','export-service',metadata_snapshot=meta)
 assert payload==before and count(r,raw)==count(r,pending)==count(r,audit)==1
 with r.engine.connect() as c:
  row=c.execute(select(raw).where(raw.c.id==sid)).mappings().one()
  assert row['payload']==payload and row['metadata_snapshot']==meta
 claim=r.claim('processor');assert claim.payload==payload
 assert r.fail(sid,claim.claim_token,'processor','mapping_pending') is True
 assert count(r,raw)==1 and r.pending_rows('queue-service')[0]['state']=='retry'
 assert all(s.project=='source-project' for s in policy.scopes)

def test_receipt_transaction_rolls_back_raw_head_queue_and_audit(store,monkeypatch):
 r,_,i,p,_=store
 def fail(*args):raise RuntimeError('synthetic transaction rollback')
 monkeypatch.setattr(r,'_audit',fail)
 with pytest.raises(RuntimeError):r.receive(i,p,'v1','service')
 assert all(count(r,t)==0 for t in [raw,head,pending,audit])

def test_outage_retry_and_late_source_correction_preserve_versions(store):
 r,_,i,p,clock=store
 a=r.receive(i,p|{'k6_1':''},'old-offline-version','service')
 assert r.receive(i,p|{'k6_1':''},'old-offline-version','service')==a
 claim=r.claim('processor',lease_seconds=5);clock[0]+=6
 replacement=r.claim('processor2',lease_seconds=5)
 with pytest.raises(QueueConflict):r.ack(a,claim.claim_token,'processor')
 assert r.ack(a,replacement.claim_token,'processor2') is True
 b=r.receive(i,p|{'k6_1':'0'},'old-offline-version','service')
 assert b!=a and count(r,raw)==2
 assert r.claim('processor3').source_revision_id==b

@pytest.mark.parametrize('grant',[False,None,1,'approved'])
def test_service_policy_exact_true_required_without_registry(store,grant):
 r,p,i,payload,_=store;p.grant=grant
 with pytest.raises(IntakeDenied):r.receive(i,payload,'v1','service')
 assert count(r,raw)==0

def test_queue_cannot_access_other_destination_same_project(store):
 r,p,i,payload,clock=store
 other=Intake(r.engine,project='source-project',destination='Tanzania',service_identity='configured-service',policy=p,clock=lambda:clock[0])
 sid=other.receive(i,payload,'v1','service')
 assert r.pending_rows('queue-service')==[]
 assert r.claim('processor') is None
 claim=other.claim('processor')
 with pytest.raises(QueueConflict):r.ack(sid,claim.claim_token,'processor')
 assert other.ack(sid,claim.claim_token,'processor') is True

@pytest.mark.parametrize('source_id',[None,123])
def test_source_identifier_present_and_native_string_required(store,source_id):
 r,_,i,p,_=store
 payload=dict(p)
 if source_id is None:payload.pop('study_id')
 else:
  i=RecordIdentity('source-project',str(source_id),'baseline','','');payload['study_id']=source_id
 with pytest.raises(ValueError):r.receive(i,payload,'v1','service')
 assert count(r,raw)==0

def test_receipt_deduplication_never_acknowledges_another_destination(store):
 r,p,i,payload,clock=store
 a=r.receive(i,payload,'v1','service')
 other=Intake(r.engine,project='source-project',destination='Tanzania',service_identity='configured-service',policy=p,clock=lambda:clock[0])
 b=other.receive(i,payload,'v1','service')
 assert a!=b
 assert r.claim('processor').source_revision_id==a
 assert other.claim('processor').source_revision_id==b
