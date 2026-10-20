"""End-to-end synthetic transport -> source/validation -> score -> review/export."""
import json
from pathlib import Path
from dataclasses import replace
import pytest
from sqlalchemy import create_engine,event,select,func
from etl.config import Settings
from etl.contracts.v31 import DICTIONARY_HEADERS
from etl.extract.production_client import ProductionRedcapClient,API_METADATA_KEYS,RedcapMetadataDrift
from etl.repository.v31 import Repository,RegistryDecision,RecordIdentity,AccessDenied,raw,derived,validated
from etl.repository.migration import upgrade
from etl.sync.v31_workflow import Workflow,DownstreamProcessor
from etl.intake.v31 import Intake,metadata as intake_metadata,raw as intake_raw
from etl.repository.participant_links import ParticipantLinks,metadata as link_metadata
C=json.loads((Path(__file__).parents[1]/'etl/contracts/data_contract_v31.json').read_text(encoding="utf-8"))

class Policy:
    def __init__(self): self.state=RegistryDecision('Ghana',True,True,'NDS-SYN-17'); self.grant=True
    def resolve(self, identity):
        if identity.participant != '00017': raise KeyError('unregistered synthetic contact')
        return self.state
    def permits(self,*a): return self.grant
    def transfer_permitted(self,identity,destination):return destination=='Ghana'

class Response:
    status_code=200
    def __init__(self,value):self.value=value
    def json(self):return self.value
class Transport:
    def __init__(self): self.rows=[];self.calls=[];self.drift=False
    def post(self,url,**kw):
        self.calls.append(kw['data'])
        if kw['data']['content']=='metadata':
            rows=[{k:f['dictionary_metadata'][h] for k,h in zip(API_METADATA_KEYS,DICTIONARY_HEADERS)} for f in C['fields']]
            if self.drift:rows[0]['field_note']='synthetic drift'
            return Response(rows)
        return Response(self.rows)

@pytest.fixture
def env():
    e=create_engine('sqlite:///:memory:')
    @event.listens_for(e,'connect')
    def fk(c,r):c.execute('PRAGMA foreign_keys=ON')
    with e.begin() as c:upgrade(c)
    p=Policy();r=Repository(e,p,storage_destination='Ghana');t=Transport()
    s=Settings(REDCAP_MOCK_ENABLED=False,REDCAP_API_TOKEN='synthetic-token-only',
               REDCAP_API_URL='https://synthetic.invalid/api/',REDCAP_PROJECT_ID='synthetic-project')
    client=ProductionRedcapClient(s,session=t,authorisation_provider=lambda scope:True,contract=C)
    context=lambda row:(row['redcap_event_name'],row.get('redcap_repeat_instrument',''),row.get('redcap_repeat_instance',''))
    class ServicePolicy:
        def authorises(self,scope):return True  # Synthetic project service grant only.
    clock=[1000.0]
    with e.begin() as c:intake_metadata.create_all(c);link_metadata.create_all(c)
    intake=Intake(e,project='synthetic-project',destination='Ghana',service_identity='synthetic-service',policy=ServicePolicy(),clock=lambda:clock[0])
    links=ParticipantLinks(e,authoriser=lambda *args:True)
    links.bind('synthetic-project','00017','NDS-SYN-17','synthetic-mapping-v1','registration-fixture')
    collector=Workflow(client,intake,project='synthetic-project',context_provider=context)
    processor=DownstreamProcessor(intake,r,links,applicability_provider=lambda identity:True)
    # Old processing assertions now deliberately exercise both distinct phases.
    class Phases:
        def sync(self,**args):
            collector.sync(**args);clock[0]+=70;return processor.process()
        @property
        def context_provider(self):return collector.context_provider
        @context_provider.setter
        def context_provider(self,value):collector.context_provider=value
        @property
        def applicability_provider(self):return processor.applicability_provider
        @applicability_provider.setter
        def applicability_provider(self,value):processor.applicability_provider=value
    w=Phases();w.collector=collector;w.processor=processor;w.intake=intake;w.clock=clock
    return e,p,r,t,w,RecordIdentity('synthetic-project','00017','baseline','','')

def row():
    data={'study_id':'00017','country':'1','redcap_event_name':'baseline'}
    for f in C['fields']:
        if f['respondent_question']:
            m=f['dictionary_metadata'];choices=m['Choices, Calculations, OR Slider Labels']
            data[f['name']]=choices.split(',',1)[0] if choices else '2'
    # Independent zero NSES raw pattern: maximum protective resources.
    for name in ['brs_01','brs_03','brs_05']:data[name]='5'
    for name in ['brs_02','brs_04','brs_06']:data[name]='1'
    for name in [f['name'] for f in C['fields'] if f['analysis_mapping'] and f['analysis_mapping'].get('NSES_dimension')=='social_support']:data[name]='7'
    for name in [f['name'] for f in C['fields'] if f['analysis_mapping'] and f['analysis_mapping'].get('NSES_dimension')=='self_efficacy']:data[name]='4'
    return data

def count(e,table):
    with e.connect() as c:return c.execute(select(func.count()).select_from(table)).scalar_one()

def test_full188_lossless_derived_replay_and_correction(env):
    e,p,r,t,w,i=env;t.rows=[row()]
    assert w.sync(source_version='synthetic-v31',full=True)['processed']==1
    out=r.export(i,'synthetic-researcher','Ghana')
    assert out['payload']==row() and out['identity']['participant']=='00017'
    assert len(set(out['payload']) & set(C['question_fields']))==188
    assert r.review(i,'synthetic-reviewer','Ghana')['stages']['screening']['complete_valid']
    with e.connect() as c:
        score=c.execute(select(derived.c.result)).scalar_one()
        assert score['scores']['NSES']['value']=={'numerator':0,'denominator':1}
    w.sync(source_version='synthetic-v31',since='2026-10-12 00:00:00')
    assert count(e,raw)==count(e,derived)==1
    assert 'dateRangeBegin' not in t.calls[-1]  # Full reconciliation, not a creation-time watermark.
    t.rows=[row()|{'k6_1':'4'}];w.sync(source_version='synthetic-v31',full=True)
    assert count(e,raw)==count(e,derived)==2
    with e.connect() as c:
        source=c.execute(select(raw).order_by(raw.c.revision)).mappings().all()
        assert source[0]['payload']['k6_1']=='0' and source[1]['payload']['k6_1']=='4'

@pytest.mark.parametrize('n',[73,78,100,152,188])
def test_progressive_flow(env,n):
    e,p,r,t,w,i=env;all=row();names=set(C['question_fields'][:n])
    t.rows=[{k:v for k,v in all.items() if k not in C['question_fields'] or k in names}]
    w.sync(source_version='synthetic-v31')
    assert len(set(r.export(i,'researcher','Ghana')['payload'])&set(C['question_fields']))==n
    assert count(e,derived)==1

def test_repeat_source_country_absent_preserved_using_current_nds_scope(env):
    e,p,r,t,w,i=env;a=row();a.pop('country');a.update(redcap_event_name='month6',redcap_repeat_instrument='neps31_yeb',redcap_repeat_instance='2');t.rows=[a]
    w.sync(source_version='synthetic-v31')
    repeated=replace(i,event='month6',instrument='neps31_yeb',instance='2')
    assert 'country' not in r.export(repeated,'researcher','Ghana')['payload']

def test_unregistered_contact_and_nds_consent_never_block_raw_receipt(env):
    e,p,r,t,w,i=env;t.rows=[row()|{'study_id':'NEW-REDCAP-CONTACT'}]
    result=w.sync(source_version='synthetic-v31')
    assert result['processed']==0 and result['deferred']==1
    assert count(e,intake_raw)==1 and count(e,raw)==0
    t.rows=[row()];w.sync(source_version='synthetic-v31');p.state=replace(p.state,consent_current=False)
    t.rows=[row()|{'k6_1':'4'}]
    assert w.sync(source_version='synthetic-v31')['deferred']>=1
    assert count(e,intake_raw)==3  # NDS consent cannot block incoming amendment.
    for action in [lambda:r.review(i,'reviewer','Ghana'),lambda:r.export(i,'researcher','Ghana')]:
        with pytest.raises(AccessDenied):action()
    assert count(e,raw)==count(e,derived)==1


def test_drift_and_missing_context_fail_before_ingestion(env):
    e,p,r,t,w,i=env;t.rows=[row()];t.drift=True
    assert w.sync(source_version='synthetic-v31')['deferred']==1
    assert count(e,intake_raw)==1  # Drift retains receipt but restricts downstream interpretation.
    assert count(e,raw)==0
    w.context_provider=None
    with pytest.raises(PermissionError):w.sync(source_version='synthetic-v31')
    assert count(e,raw)==0


@pytest.mark.parametrize('code,country',[('1','Ghana'),('2','Sierra Leone'),('3','Tanzania')])
def test_each_country_requires_explicit_current_storage_and_export_scope(env,code,country):
    e,p,r,t,w,i=env;p.state=RegistryDecision(country,True,True,'NDS-SYN-17')
    p.transfer_permitted=lambda identity,destination:destination==country
    r.storage_destination=country;t.rows=[row()|{'country':code}]
    w.sync(source_version='synthetic-v31')
    assert r.export(i,'researcher',country)['payload']['country']==code
    with pytest.raises(AccessDenied):r.export(i,'researcher','unapproved-destination')


def test_nds_unavailable_then_later_registration_replays_durable_source(env):
    e,p,r,t,w,i=env;t.rows=[row()];r.adapter=None
    assert w.sync(source_version='synthetic-v31')['deferred']==1
    assert count(e,intake_raw)==1 and count(e,raw)==0
    r.adapter=p;w.clock[0]+=70
    assert w.processor.process()['processed']==1
    assert count(e,intake_raw)==1 and count(e,raw)==count(e,derived)==1
    exported=r.export(i,'researcher','Ghana')
    assert exported['payload']['study_id']=='00017' and exported['nds_participant_id']=='NDS-SYN-17'
