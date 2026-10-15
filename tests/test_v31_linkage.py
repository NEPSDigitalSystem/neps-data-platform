import json
from pathlib import Path
import pytest
from etl.contracts.linkage import RedcapParticipantKey

CONTRACT = json.loads((Path(__file__).parents[1] / 'etl/contracts/data_contract_v31.json').read_text())


def test_redcap_issued_id_preserved_and_project_namespaced():
    key = RedcapParticipantKey.from_record('synthetic-project-a', {'study_id': '00017'}, CONTRACT)
    assert key.source_id == '00017' and key.issuer == 'REDCap'
    assert key != RedcapParticipantKey.from_record('synthetic-project-b', {'study_id':'00017'}, CONTRACT)
    assert CONTRACT['participant_linkage']['nds_authority'] == ['registration', 'consent', 'processing_permissions']


@pytest.mark.parametrize('value', [None, '', 17, False])
def test_missing_or_numeric_id_is_never_minted_or_coerced(value):
    with pytest.raises(ValueError):
        RedcapParticipantKey.from_record('synthetic-project', {'study_id':value}, CONTRACT)
