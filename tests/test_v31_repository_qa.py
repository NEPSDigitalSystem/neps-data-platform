"""Independent repository QA; disposable SQLite and synthetic policy only."""
from dataclasses import replace
import pytest
from sqlalchemy import create_engine,event,select,func
from sqlalchemy.exc import IntegrityError
from etl.repository.v31 import Repository,RecordIdentity,RegistryDecision,AccessDenied,raw,validated,derived,audit
from etl.repository.migration import upgrade

class Policy:
 def __init__(self):self.state=RegistryDecision('Ghana',True,True);self.grant=True;self.transfer=True
 def resolve(self,i):return self.state
 def permits(self,*args):return self.grant
 def transfer_permitted(self,*args):return self.transfer
@pytest.fixture
def independent_repo():
 e=create_engine('sqlite:///:memory:')
 @event.listens_for(e,'connect')
 def fk(c,r):c.execute('PRAGMA foreign_keys=ON')
 with e.begin() as c:upgrade(c)
 p=Policy();r=Repository(e,p,storage_destination='Ghana')
 i=RecordIdentity('synthetic-project','QA-1','baseline','neps31_yeb','1')
 payload={'study_id':'QA-1','country':'1','redcap_event_name':'baseline','redcap_repeat_instrument':'neps31_yeb','redcap_repeat_instance':'1','k6_1':'0'}
 return r,p,i,payload

def rows(r,t):
 with r.engine.connect() as c:return c.execute(select(func.count()).select_from(t)).scalar_one()
@pytest.mark.parametrize('state', [RegistryDecision('Ghana','false',True),RegistryDecision('Ghana',True,1)])
def test_registry_permission_must_be_explicit_boolean(independent_repo,state):
 r,p,i,payload=independent_repo;p.state=state
 with pytest.raises(AccessDenied):r.ingest(i,payload,'v1')
 assert rows(r,raw)==0
@pytest.mark.parametrize('grant,transfer', [('approved',True),(True,'approved'),(1,True)])
def test_adapter_grants_require_exact_true(independent_repo,grant,transfer):
 r,p,i,payload=independent_repo;p.grant=grant;p.transfer=transfer
 with pytest.raises(AccessDenied):r.ingest(i,payload,'v1')
 assert rows(r,raw)==0

def test_corrections_keep_history_and_source_distinctions(independent_repo):
 r,p,i,payload=independent_repo
 a=r.ingest(i,payload,'v1');b=r.ingest(i,payload|{'k6_1':None},'v1')
 c=r.ingest(i,{k:v for k,v in payload.items() if k!='k6_1'},'v1')
 assert len({a,b,c})==3
 with r.engine.connect() as conn:
  history=conn.execute(select(raw).order_by(raw.c.revision)).mappings().all()
  assert [x['revision'] for x in history]==[1,2,3]
  assert history[0]['payload']['k6_1']=='0'
  assert history[1]['payload']['k6_1'] is None
  assert 'k6_1' not in history[2]['payload']
  assert len({x['change_hash'] for x in history})==3

def test_derived_revocation_denied_without_write(independent_repo):
 r,p,i,payload=independent_repo;sid=r.ingest(i,payload,'v1')
 p.state=replace(p.state,consent_current=False)
 with pytest.raises(AccessDenied):r.store_derived(sid,'calc-v1',{})
 assert rows(r,derived)==0 and rows(r,audit)==1

def test_source_foreign_keys_reject_orphan_derived(independent_repo):
 r,_,_,_=independent_repo
 with r.engine.begin() as c:
  with pytest.raises(IntegrityError):c.execute(derived.insert().values(id='synthetic-orphan',source_id='absent',calculation_version='v1',result={}))
 assert rows(r,derived)==0
