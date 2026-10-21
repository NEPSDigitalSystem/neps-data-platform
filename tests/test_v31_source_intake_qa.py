"""Independent native source snapshot QA; synthetic full-project export only."""
import copy
import pytest
from test_v31_connector import Session,Response,settings,native_metadata
from etl.extract.production_client import ProductionRedcapClient,RedcapAuthorisationError,RedcapClientError

def test_changed_actual_metadata_extra_consent_transfers_all_without_nds():
 metadata=native_metadata()
 metadata[0]['field_name']='source_id'
 # Synthetic extra actual instrument field, not a proposed change to supplied dictionary.
 metadata.append(dict(metadata[-1],field_name='SYNTHETIC_observed_consent',form_name='SYNTHETIC_source_consent'))
 rows=[{'source_id':'REDCAP-INDEPENDENT-1','SYNTHETIC_observed_consent':'observed-code',
        'redcap_event_name':'baseline','redcap_repeat_instance':'','redcap_repeat_instrument':'','k6_1':''}]
 original=copy.deepcopy(rows);scopes=[]
 transport=Session(Response(metadata),Response(rows),Response(metadata))
 client=ProductionRedcapClient(settings(),session=transport,authorisation_provider=lambda s:scopes.append(s) or True,sleep=lambda _:None)
 result=client.export_source_snapshot()
 assert result.records==original and result.record_id_field=='source_id'
 assert result.metadata==metadata and result.contract_drift
 assert set(next(s for s in scopes if s.operation=='record').fields)=={r['field_name'] for r in metadata}
 assert next(s for s in scopes if s.operation=='record').full_project_records is True
 data=next(kw['data'] for url,kw in transport.calls if kw['data']['content']=='record')
 assert not any(k.startswith(('fields[','forms[','records[')) for k in data)
 assert data['exportSurveyFields']=='true'
 assert data['rawOrLabel']=='raw' and data['rawOrLabelHeaders']=='raw'

def test_snapshot_policy_denied_before_record_http():
 transport=Session(Response(native_metadata()))
 client=ProductionRedcapClient(settings(),session=transport,authorisation_provider=lambda s:s.operation=='metadata',sleep=lambda _:None)
 with pytest.raises(RedcapAuthorisationError):client.export_source_snapshot()
 assert len(transport.calls)==1

@pytest.mark.parametrize('row',[{'study_id':None},{'study_id':'valid','UNVERIFIED_out_of_scope':'value'}])
def test_snapshot_rejects_identifier_or_unapproved_response_scope(row):
 transport=Session(Response(native_metadata()),Response([row]),Response(native_metadata()))
 client=ProductionRedcapClient(settings(),session=transport,authorisation_provider=lambda s:True,sleep=lambda _:None)
 with pytest.raises(RedcapClientError):client.export_source_snapshot()
