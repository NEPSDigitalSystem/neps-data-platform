"""Configured independent collector; synthetic HTTP/SQLite only."""
from sqlalchemy import create_engine,select,func
import pytest
from etl.config import Settings
from etl.intake.v31 import metadata,raw
from etl.sync.source_runtime import build_collector,SourceServiceGrant
from test_v31_connector import Session,Response,native_metadata


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
