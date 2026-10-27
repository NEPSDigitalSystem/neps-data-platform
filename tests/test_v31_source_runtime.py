"""Configured independent collector; synthetic HTTP/SQLite only."""
from sqlalchemy import create_engine,select,func
import pytest
from etl.config import Settings
from etl.intake.v31 import metadata,raw
from etl.sync.source_runtime import build_collector,SourceServiceGrant
from test_v31_connector import Session,Response,native_metadata
from test_v31_workflow import env, row


def config(**change):
    values=dict(REDCAP_MOCK_ENABLED=False,REDCAP_API_TOKEN='synthetic-source-key',
                REDCAP_API_URL='https://synthetic.invalid/api/',REDCAP_PROJECT_ID='source-only-project',
                SOURCE_INTAKE_ENABLED=True,SOURCE_DESTINATION='synthetic-approved-store',
                SOURCE_SERVICE_IDENTITY='source-service-fixture',SOURCE_EVENT_MODE='classic')
    values.update(change);return Settings(**values)


def test_configured_runtime_receives_before_any_nds_lifecycle():
    e=create_engine('sqlite:///:memory:')
    with e.begin() as c:metadata.create_all(c)
    row={'study_id':'SOURCE-NEW-0001','country':'1','k6_1':'0','neps31_screening_complete':'2'}
    s=Session(Response(native_metadata()),Response([row]),Response(native_metadata()))
    collector=build_collector(config(),engine=e,session=s)
    assert collector.sync(source_version='synthetic-current-source')['received']==1
    with e.connect() as c:
        assert c.execute(select(func.count()).select_from(raw)).scalar_one()==1
        assert c.execute(select(raw.c.payload)).scalar_one()==row


@pytest.mark.parametrize('change',[{'SOURCE_INTAKE_ENABLED':False},{'SOURCE_DESTINATION':None},
                                    {'SOURCE_SERVICE_IDENTITY':None},{'SOURCE_EVENT_MODE':'unverified'},
                                    {'REDCAP_MOCK_ENABLED':True}])
def test_incomplete_source_configuration_never_starts_http(change):
    s=Session()
    with pytest.raises(PermissionError):build_collector(config(**change),session=s)
    assert not s.calls


def test_event_configuration_is_source_only_and_checks_repeat_types():
    g=SourceServiceGrant(config(SOURCE_EVENT_MODE='longitudinal'))
    assert g.context({'redcap_event_name':'baseline','redcap_repeat_instrument':'neps31_yeb','redcap_repeat_instance':2})==('baseline','neps31_yeb','2')
    with pytest.raises(ValueError):g.context({'redcap_event_name':''})
    with pytest.raises(ValueError):g.context({'redcap_event_name':'baseline','redcap_repeat_instance':True})


def test_auto_context_preserves_later_classic_to_longitudinal_and_repeating_changes():
    g=SourceServiceGrant(config(SOURCE_EVENT_MODE='auto'))
    assert g.context({})==('','','')
    assert g.context({'redcap_event_name':'new_wave','redcap_repeat_instrument':'new_form','redcap_repeat_instance':3})==('new_wave','new_form','3')
    with pytest.raises(ValueError):g.context({'redcap_event_name':None})


def test_configured_database_engine_redacts_source_parameters_without_connecting():
    from etl.load.db import create_db_engine
    engine=create_db_engine(config(DATABASE_URL='sqlite:///:memory:'))
    assert engine.hide_parameters is True
    assert engine.echo is False
    engine.dispose()


@pytest.mark.parametrize('instance', ['2', 2])
def test_native_repeat_instance_survives_receipt_processing_and_export(env, instance):
    from dataclasses import replace
    from etl.repository.v31 import raw as research_raw, derived
    from etl.intake.v31 import pending

    engine, _, repository, transport, workflow, identity = env
    workflow.collector.context_provider = SourceServiceGrant(
        config(SOURCE_EVENT_MODE='auto')).context
    source = row() | {'redcap_event_name': 'month6',
                      'redcap_repeat_instrument': 'neps31_yeb',
                      'redcap_repeat_instance': instance}
    transport.rows = [source]
    assert workflow.collector.sync(source_version='synthetic-repeat-v1')['received'] == 1
    assert workflow.processor.process() == {'processed': 1, 'deferred': 0}

    repeated = replace(identity, event='month6', instrument='neps31_yeb', instance='2')
    exported = repository.export(repeated, 'synthetic-reviewer', 'Ghana')
    assert exported['payload'] == source
    assert type(exported['payload']['redcap_repeat_instance']) is type(instance)
    with engine.connect() as connection:
        receipt = connection.execute(select(raw)).mappings().one()
        research = connection.execute(select(research_raw)).mappings().one()
        score = connection.execute(select(derived.c.result)).scalar_one()
        assert receipt['payload'] == research['payload'] == source
        assert receipt['identity']['instance'] == research['identity']['instance'] == '2'
        assert research['intake_revision_id'] == receipt['id']
        assert score['intake_revision_id'] == receipt['id']
        assert connection.execute(select(pending.c.state)).scalar_one() == 'acknowledged'
