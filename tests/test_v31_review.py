import json
from pathlib import Path
from etl.analytics.v31_review import completion
C = json.loads((Path(__file__).parents[1] / 'etl/contracts/data_contract_v31.json').read_text())


def test_complete_screening_can_coexist_with_115_unanswered():
    values = {name:'synthetic-marker-not-returned' for name in C['core_73_fields']}
    r = completion(C, values, values, {})
    assert [v['expected'] for v in r['stages'].values()] == [73,5,74,36]
    assert r['stages']['screening']['complete_valid']
    assert not r['all_valid']
    assert 'synthetic-marker' not in str(r)


def test_188_coverage_and_explicit_absent_null_empty_invalid():
    payload = {name:'1' for name in C['question_fields']}
    assert completion(C,payload,payload,{})['all_valid']
    names=C['core_73_fields']
    payload.pop(names[0]);payload[names[1]]=None;payload[names[2]]=''
    r=completion(C,payload,payload,{names[3]:'invalid_code'})
    assert r['stages']['screening']['states'] == {'absent':1,'null':1,'empty':1,'invalid_code':1,'valid':69}
    assert not r['all_valid']
