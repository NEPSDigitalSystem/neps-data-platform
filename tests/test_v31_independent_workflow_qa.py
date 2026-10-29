"""Independent phase separation and source retention tests."""
import copy
import pytest
from sqlalchemy import select
from test_v31_workflow import env,row,count,C
from etl.intake.v31 import raw as intake_raw,pending,audit as intake_audit,IntakeUnavailable
from etl.extract.production_client import RedcapClientError
from etl.repository.v31 import raw
from etl.contracts.survey_consent import extend
from etl.contracts.v31 import NAME,BRANCH,TYPE,CHOICES
from etl.repository.v31 import branch_state

def test_collector_never_calls_nds_repository_links_or_consent(env,monkeypatch):
 e,p,r,t,w,i=env;t.rows=[row()|{'study_id':'REDCAP-UNKNOWN-INDEPENDENT'}]
 def forbidden(*a,**k):raise AssertionError('NDS callback during source intake')
 monkeypatch.setattr(r,'ingest',forbidden)
 monkeypatch.setattr(w.processor.links,'resolve',forbidden)
 p.state=None
 result=w.collector.sync(source_version='stable-source-metadata-v1',since='2099-01-01',full=False)
 assert result['received']==1 and result['full_reconciliation'] is True
 assert count(e,intake_raw)==1 and count(e,raw)==0
 assert 'dateRangeBegin' not in t.calls[-1]
 with e.connect() as c:assert c.execute(select(pending.c.state)).scalar_one()=='pending'

def test_midbatch_receipt_failure_does_not_lose_already_durable_data(env,monkeypatch):
 e,p,r,t,w,i=env
 # This earlier identity is omitted by the next export. An interrupted export
 # must not mark it absent before all incoming records are durable.
 t.rows=[row()|{'study_id':'PREVIOUS-OFFLINE-ID'}]
 w.collector.sync(source_version='stable-v1')
 t.rows=[row(),row()|{'study_id':'SECOND-OFFLINE-ID'}]
 original=w.intake.receive;attempt=[0]
 def interrupted(*a,**k):
  attempt[0]+=1
  if attempt[0]==2:raise IntakeUnavailable('synthetic durable store outage')
  return original(*a,**k)
 monkeypatch.setattr(w.intake,'receive',interrupted)
 with pytest.raises(IntakeUnavailable):w.collector.sync(source_version='stable-v1')
 assert count(e,intake_raw)==2 and count(e,raw)==0
 with e.connect() as c:
  assert c.execute(select(intake_audit).where(
   intake_audit.c.action=='not_seen_in_full_export')).first() is None
 monkeypatch.setattr(w.intake,'receive',original)
 assert w.collector.sync(source_version='stable-v1')['received']==2
 assert count(e,intake_raw)==3 and count(e,pending)==3
 with e.connect() as c:
  assert len(c.execute(select(intake_audit).where(
   intake_audit.c.action=='not_seen_in_full_export')).all())==1


@pytest.mark.parametrize('records', [None, {}, 'malformed-success-body', [None],
                                   [row(), {'study_id': ''}]])
def test_malformed_native_export_cannot_write_a_partial_batch(env, records):
 e,p,r,t,w,i=env;t.rows=records
 with pytest.raises(RedcapClientError):
  w.collector.sync(source_version='synthetic-malformed-v1')
 assert count(e,intake_raw)==count(e,pending)==count(e,intake_audit)==count(e,raw)==0


def test_invalid_later_repeat_context_prevents_all_receipts(env):
 from etl.sync.source_runtime import SourceServiceGrant
 from test_v31_source_runtime import config
 e,p,r,t,w,i=env
 w.collector.context_provider=SourceServiceGrant(config(SOURCE_EVENT_MODE='auto')).context
 t.rows=[row(),row()|{'study_id':'INVALID-REPEAT','redcap_repeat_instance':True}]
 with pytest.raises(ValueError):
  w.collector.sync(source_version='synthetic-malformed-context-v1')
 assert count(e,intake_raw)==count(e,pending)==count(e,intake_audit)==count(e,raw)==0

def test_corrected_offline_data_retained_while_nds_downstream_withdrawn(env):
 e,p,r,t,w,i=env
 t.rows=[row()];w.collector.sync(source_version='stable-v1')
 from dataclasses import replace
 p.state=replace(p.state,consent_current=False)
 assert w.processor.process()['deferred']==1
 w.clock[0]+=70;t.rows=[row()|{'k6_1':'4'}]
 w.collector.sync(source_version='stable-v1',since='2099-01-01')
 assert count(e,intake_raw)==2 and count(e,raw)==0
 with e.connect() as c:
  source=c.execute(select(intake_raw).order_by(intake_raw.c.revision)).mappings().all()
  assert [s['payload']['k6_1'] for s in source]==['0','4']

def test_proposed_consent_first_and_original188_unchanged_source_metadata():
 dictionary=[f['dictionary_metadata'] for f in C['fields']]
 before=copy.deepcopy(dictionary);proposed=extend(dictionary)
 assert dictionary==before and len(proposed)==224
 assert proposed[0][NAME]=='study_id'
 corrected={'Section Header','Field Label','Field Note'}
 assert {k:v for k,v in proposed[0].items() if k not in corrected}=={k:v for k,v in dictionary[0].items() if k not in corrected}
 assert proposed[0]['Field Note']=='REDCap-issued survey record identifier.'
 assert 'NDS' not in proposed[0]['Field Note'] and 'import' not in proposed[0]['Field Note'].lower()
 consent=proposed[1]
 assert consent[NAME]=='survey_consent' and consent[TYPE]=='radio'
 assert consent[CHOICES]=='1, Yes, I consent | 0, No, I do not consent'
 assert consent['Required Field?']=='y'
 assert [r[NAME] for r in proposed[2:]]==[r[NAME] for r in dictionary[1:]]
 for original,changed in zip(dictionary[1:],proposed[2:]):
  assert {k:v for k,v in original.items() if k!=BRANCH}=={k:v for k,v in changed.items() if k!=BRANCH}
  assert changed[BRANCH].startswith("[survey_consent] = '1'")
  values={f['name']:'synthetic-nonmatching-code' for f in C['fields']}
  values['survey_consent']='0'
  assert branch_state(changed[BRANCH],values) is False
 assert len(set(C['question_fields'])&{r[NAME] for r in proposed})==188

@pytest.mark.parametrize('consent,expected_score',[('1',True),('0',False)])
def test_proposed_actual_source_consent_controls_processing_not_receipt(env,monkeypatch,consent,expected_score):
 e,p,r,t,w,i=env
 from test_v31_workflow import Response
 from etl.extract.production_client import API_METADATA_KEYS
 from etl.contracts.v31 import DICTIONARY_HEADERS
 from etl.repository.v31 import derived,validated
 proposed=extend([f['dictionary_metadata'] for f in C['fields']])
 native=[{key:meta[header] for header,key in zip(DICTIONARY_HEADERS,API_METADATA_KEYS)} for meta in proposed]
 source=row()|{'survey_consent':consent}
 def post(url,**kwargs):
  t.calls.append(kwargs['data'])
  return Response(native if kwargs['data']['content']=='metadata' else [source])
 monkeypatch.setattr(t,'post',post)
 w.processor.accepted_metadata=proposed
 received=w.collector.sync(source_version='synthetic-proposed-consent-v1')
 assert received['received']==1 and count(e,intake_raw)==1 and count(e,raw)==0
 assert w.processor.process()['processed']==1
 with e.connect() as c:
  actual=c.execute(select(derived.c.result)).scalar_one()
  layer=c.execute(select(validated)).mappings().one()
  original=c.execute(select(intake_raw)).mappings().one()
  assert original['payload']==source and original['metadata_snapshot']==native
  value=actual['scores']['NSES']['value']
  assert (value is not None)==expected_score
  assert layer['values']['survey_consent']==consent
  if not expected_score:assert layer['issues']['k6_1']=='inapplicable'
  assert actual['source_sha256']
  assert actual['intake_revision_id']==original['id']
  assert actual['source_metadata_sha256']==original['metadata_hash']
  assert actual['nds_participant_id']=='NDS-SYN-17'
  assert actual['mapping_version']=='synthetic-mapping-v1'
  processed=c.execute(select(raw)).mappings().one()
  assert processed['intake_revision_id']==original['id']
  assert processed['source_metadata']==proposed
  from etl.repository.v31 import digest
  assert processed['source_metadata_hash']==digest(proposed)
  assert actual['provisional'] is True
