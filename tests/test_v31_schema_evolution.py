"""Source changes remain transferable; observed schema is versioned, not guessed."""
import copy
import pytest
from sqlalchemy import create_engine,select
from etl.extract.production_client import ProductionRedcapClient,RedcapClientError
from etl.intake.v31 import Intake,RecordIdentity,metadata as intake_metadata,raw
from test_v31_connector import native_metadata,settings,Session,Response


def client(metadata,rows):
    return ProductionRedcapClient(settings(),session=Session(Response(metadata),Response(rows),Response(metadata)),
                                  authorisation_provider=lambda scope:True,sleep=lambda _:None)


@pytest.mark.parametrize('change',['added','renamed','removed','codes','type','branch','api_extension'])
def test_current_source_schema_changes_do_not_trigger_fixed223_transfer_gate(change):
    m=native_metadata();row={'study_id':'SOURCE-0001','k6_1':'3','household_language':'native text'}
    field=next(f for f in m if f['field_name']=='household_language')
    if change=='added':
        m.append(dict(field,field_name='synthetic_new_context'));row['synthetic_new_context']='new raw value'
    if change=='renamed':
        field['field_name']='synthetic_renamed_context';row['synthetic_renamed_context']=row.pop('household_language')
    if change=='removed':
        m.remove(field);row.pop('household_language')
    if change=='codes':
        next(f for f in m if f['field_name']=='k6_1')['select_choices_or_calculations']='3, Revised source description'
    if change=='type':
        field.update(field_type='checkbox',select_choices_or_calculations='1, Source option');row.pop('household_language');row['household_language___1']='1'
    if change=='branch':field['branching_logic']="[synthetic_source_gate] = '1'"
    if change=='api_extension':field['synthetic_future_metadata_key']='retained metadata'
    snapshot=client(m,[row]).export_source_snapshot()
    assert snapshot.records==[row] and snapshot.metadata==m and snapshot.contract_drift


def test_schema_change_during_export_refreshes_before_receipt():
    old=native_metadata();new=copy.deepcopy(old);new.append(dict(new[-1],field_name='synthetic_added_mid_export'))
    rows=[{'study_id':'0001','synthetic_added_mid_export':'original raw answer'}]
    transport=Session(Response(old),Response(rows),Response(new),Response(new),Response(rows),Response(new))
    c=ProductionRedcapClient(settings(),session=transport,authorisation_provider=lambda scope:True,sleep=lambda _:None)
    snapshot=c.export_source_snapshot()
    assert snapshot.metadata==new and snapshot.records==rows
    assert sum(kw['data']['content']=='record' for url,kw in transport.calls)==2
    assert all(not any(k.startswith(('fields[','forms[','records[')) for k in kw['data']) for url,kw in transport.calls)


def test_continuous_schema_churn_is_bounded_and_can_be_retried():
    responses=[]
    for n in range(3):
        before=native_metadata();after=copy.deepcopy(before)
        before[0]['field_note']=str(n*2);after[0]['field_note']=str(n*2+1)
        responses += [Response(before),Response([{'study_id':'0001'}]),Response(after)]
    transport=Session(*responses)
    c=ProductionRedcapClient(settings(),session=transport,authorisation_provider=lambda scope:True,sleep=lambda _:None)
    with pytest.raises(RedcapClientError,match='retry collection'):c.export_source_snapshot()
    assert len(transport.calls)==9


def test_old_and_new_definitions_and_original_responses_remain_in_receipt_history():
    e=create_engine('sqlite:///:memory:')
    with e.begin() as c:intake_metadata.create_all(c)
    policy=type('SyntheticService',(),{'authorises':lambda self,scope:True})()
    intake=Intake(e,project='synthetic-project',destination='synthetic-store',service_identity='fixture',policy=policy)
    identity=RecordIdentity('synthetic-project','0001')
    old=native_metadata();new=copy.deepcopy(old);next(f for f in new if f['field_name']=='k6_1')['field_note']='new source version'
    for m,code in [(old,'0'),(new,'4')]:
        snapshot=client(m,[{'study_id':'0001','k6_1':code}]).export_source_snapshot()
        intake.receive(identity,snapshot.records[0],'actual-observed-metadata','collector',metadata_snapshot=snapshot.metadata)
    with e.connect() as c:
        history=c.execute(select(raw).order_by(raw.c.revision)).mappings().all()
        assert [r['payload']['k6_1'] for r in history]==['0','4']
        assert history[0]['metadata_snapshot']==old and history[1]['metadata_snapshot']==new
        assert history[0]['metadata_hash']!=history[1]['metadata_hash']


from test_v31_workflow import env, row, count
from etl.repository.v31 import derived
from etl.contracts.v31 import DICTIONARY_HEADERS
from etl.extract.production_client import API_METADATA_KEYS


def test_reviewed_new_metadata_version_can_process_queued_revision_without_reimport(env):
    e,p,r,t,w,i=env
    metadata=native_metadata()
    next(f for f in metadata if f['field_name']=='household_language')['field_note']='new reviewed source version'
    data=row()
    transport=Session(Response(metadata),Response([data]),Response(metadata))
    w.collector.client=ProductionRedcapClient(settings(redcap_project_id='synthetic-project'),session=transport,
                                             authorisation_provider=lambda scope:True,sleep=lambda _:None)
    result=w.collector.sync(source_version='synthetic-new-version')
    assert result['received']==1
    assert w.processor.process()['deferred']==1
    assert count(e,derived)==0
    w.processor.approved_metadata_versions[result['metadata_sha256']]={
        'version':'synthetic-reviewed-schema-v2',
        'metadata':[{h:f[k] for h,k in zip(DICTIONARY_HEADERS,API_METADATA_KEYS)} for f in metadata]}
    w.clock[0]+=70
    assert w.processor.process()['processed']==1
    assert count(e,raw)==1
    with e.connect() as c:
        output=c.execute(select(derived.c.result)).scalar_one()
        source=c.execute(select(raw.c.id)).scalar_one()
        assert output['metadata_policy_version']=='synthetic-reviewed-schema-v2'
        assert output['intake_revision_id']==source
        assert output['source_metadata_sha256']==result['metadata_sha256']
