"""Source-specific validation and policy boundaries, using synthetic inputs."""
import copy
import json
from pathlib import Path

import pytest
from sqlalchemy import select

from etl.validation.v31_validator import validate, validate_scores
from etl.scoring.v31 import Scorer
from etl.sync.v31_workflow import serialise
from etl.repository.v31 import AccessDenied, derived, validated
from test_v31_repository import setup, base, count
from test_v31_workflow import env, row

C = json.loads((Path(__file__).parents[1] / 'etl/contracts/data_contract_v31.json').read_text(encoding='utf-8'))
GOLD = json.loads((Path(__file__).parent / 'fixtures/SCORING_GOLDEN.json').read_text(encoding='utf-8'))
CORE = next(c['responses'] for c in GOLD['cases'] if c['id'] == 'minimum_nses')


def check(data, **kwargs):
    return validate(data, C, **kwargs)


@pytest.mark.parametrize('age,eligible', [('11', False), ('12', True), ('19', True), ('20', True), ('24', True), ('25', False)])
def test_approved_age_range_and_separate_imported_layer(age, eligible):
    result = check({'age_years': age})
    assert result.age_eligible is eligible
    assert 'age_years' not in result.values
    assert result.payload == {'age_years': age}
    assert ('V11' in [i.rule for i in result.issues]) is (not eligible)


@pytest.mark.parametrize('raw', [True, 12, 12.0, '12.0', '12 years', ' 12', '12 ', 'NaN', '１２', [], {}])
def test_age_transport_types_are_not_silently_coerced(raw):
    result = check({'age_years': raw})
    assert result.states['age_years'] == 'invalid'
    assert result.age_eligible is False


@pytest.mark.parametrize('data,state', [({}, 'absent'), ({'age_years': None}, 'null'), ({'age_years': ''}, 'empty')])
def test_unknown_age_stays_unknown(data, state):
    result = check(data)
    assert result.states['age_years'] == state
    assert result.age_eligible is None


@pytest.mark.parametrize('name,lower,upper', [('epi_expectations_1',1,5), ('esi_food_1',0,4), ('k6_1',0,4), ('sbi_help_1',1,5), ('brs_02',1,5), ('mspss_01',1,7), ('gse_01',1,4)])
def test_all_actual_scale_boundaries(name, lower, upper):
    for value in (lower, upper):
        result = check({name: str(value)})
        assert result.values[name] == str(value)
    for value in (lower-1, upper+1, 96, 98, 99):
        result = check({name: str(value)})
        assert result.states[name] == 'invalid'
        assert name not in result.values


def test_semantic_missingness_only_follows_declared_labels_or_explicit_evidence():
    result = check({'sex_report':'99', 'study_resident':'98', 'willing_24m':'96', 'self_school_perf':'96',
                    'epi_expectations_1':'99', 'currently_school':'1'})
    assert {n: result.states[n] for n in ('sex_report','study_resident','willing_24m','self_school_perf','epi_expectations_1')} == {
        'sex_report':'refused','study_resident':'unknown','willing_24m':'not_applicable',
        'self_school_perf':'not_applicable','epi_expectations_1':'invalid'}
    for reason in ('missing','refused','unknown','not_applicable','invalid'):
        evidence = {'brs_02': reason}
        result = check(CORE, missingness=evidence)
        assert result.states['brs_02'] == reason
        assert 'brs_02' not in result.values
        assert evidence == {'brs_02': reason}
    with pytest.raises(ValueError):
        check({}, missingness={'invented': 'refused'})
    with pytest.raises(ValueError):
        check({}, missingness={'brs_02': 'guessed'})


def test_every_declared_special_code_matches_its_label_without_becoming_a_global_rule():
    expected = {'Prefer not to answer':'refused', 'Prefer not':'refused', 'Do not know':'unknown', 'Unsure':'unknown',
                'Not applicable':'not_applicable', 'Never attended':'not_applicable',
                'Not attending school/training':'not_applicable', 'No such responsibilities':'not_applicable',
                'No such family':'not_applicable', 'Not available locally':'not_applicable'}
    for field in C['fields']:
        meta = copy.deepcopy(field['dictionary_metadata'])
        meta['Branching Logic (Show field only if...)'] = ''
        for part in meta['Choices, Calculations, OR Slider Labels'].split('|'):
            if ',' not in part:
                continue
            code, label = (s.strip() for s in part.split(',',1))
            if code in ('96','98','99'):
                result = check({field['name']:code}, source_fields={field['name']:meta})
                assert result.states[field['name']] == expected.get(label,'valid')
    # The same numeric code with a different reviewed label remains ordinary.
    meta = copy.deepcopy(C['fields'][0]['dictionary_metadata'])
    meta.update({'Field Type':'radio', 'Choices, Calculations, OR Slider Labels':'99, An ordinary category'})
    assert check({'new_field':'99'}, source_fields={'new_field':meta}).states['new_field'] == 'valid'


@pytest.mark.parametrize('number', ['2','98','99','1000000'])
def test_open_attack_count_is_not_a_missing_sentinel(number):
    data = {'attack_12m':'2','attack_freq_missing':'1','attack_freq':number}
    result = check(data)
    assert result.values['attack_freq'] == number
    assert result.states['attack_freq'] == 'valid'


def test_attack_count_control_and_invalid_gate_are_not_guessed():
    for control, state in [('98','unverified'), ('99','unverified')]:
        result = check({'attack_12m':'2','attack_freq_missing':control,'attack_freq':'5'})
        assert result.states['attack_freq'] == state
        assert 'attack_freq' not in result.values
    assert check({'attack_12m':'2','attack_freq_missing':'1','attack_freq':'1'}).states['attack_freq'] == 'invalid'
    assert check({'currently_school':'0','epix_exams_1':'1'}).states['epix_exams_1'] == 'not_applicable'
    assert check({'currently_school':'99','epix_exams_1':'1'}).states['epix_exams_1'] == 'unverified'
    assert check({'currently_school':'1','epix_exams_1':'1'}, missingness={'currently_school':'unknown'}).states['epix_exams_1'] == 'unverified'


@pytest.mark.parametrize('code,country', [('1','Ghana'), ('2','Sierra Leone'), ('3','Tanzania')])
def test_country_codes_are_native_and_do_not_grant_permission(code, country):
    result = check({'country':code})
    assert result.states['country'] == 'valid'
    assert 'country' not in result.values
    assert 'processing_allowed' not in result.summary()
    assert check({'country':country}).states['country'] == 'invalid'


@pytest.mark.parametrize('code', ['0','1','2'])
def test_completion_is_a_code_and_does_not_replace_core_completeness(code):
    result = check(CORE | {'screen_form_complete':code})
    assert result.states['screen_form_complete'] == 'valid'
    assert all(n in result.values for n in C['core_73_fields'])
    assert result.states[C['question_fields'][-1]] == 'absent'
    assert not any('permission' in name for name in result.summary())
    assert check({'screen_form_complete':code}).states['k6_1'] == 'absent'


@pytest.mark.parametrize('raw', ['3','99',2,True])
def test_invalid_form_completion(raw):
    result = check({'screen_form_complete':raw})
    assert result.states['screen_form_complete'] == 'invalid'
    assert any(i.rule == 'V08' for i in result.issues)


@pytest.mark.parametrize('name,valid,invalid', [
    ('household_members',['0','123456'],['-1','1.5',1,True]),
    ('brs_raw',['1','2.5','5'],['0.9','5.1','NaN','Infinity',2.5]),
    ('gse_raw',['10','40'],['9','41']),
    ('screen_date',['2024-02-29','2026-10-23'],['2026-02-29','2026-2-1','20261023','2026-10-23T00:00:00']),
])
def test_native_text_numeric_and_date_definitions(name, valid, invalid):
    for value in valid:
        assert check({name:value}).states[name] == 'valid'
    for value in invalid:
        assert check({name:value}).states[name] == 'invalid'


def test_original_key_presence_extra_fields_and_nested_values_are_preserved():
    data = {'k6_1':None, 'k6_2':'', 'future_field':{'nested':['original']}, 'household_language':'Synthetic language'}
    before = copy.deepcopy((data,C))
    result = check(data)
    assert (data,C) == before
    assert result.payload == data
    assert result.states['k6_1'] == 'null' and result.states['k6_2'] == 'empty' and result.states['k6_3'] == 'absent'
    assert result.states['future_field'] == 'unknown_field'
    assert 'future_field' not in result.values
    result.payload['future_field']['nested'].append('changed copy')
    assert data == before[0]
    assert check(data).summary() == check(data).summary()
    issue = next(i for i in result.issues if i.field == 'future_field')
    assert (issue.rule,issue.severity,issue.observed_state,issue.blocks_field) == ('V06','warning','unknown_field',True)


def test_reviewed_checkbox_metadata_and_unsupported_branch():
    meta = copy.deepcopy(C['fields'][0]['dictionary_metadata'])
    meta.update({'Field Type':'checkbox','Choices, Calculations, OR Slider Labels':'1, First | 2, Second'})
    for value,expected in [({'1':'1','2':'0'},'valid'), ({'3':'1'},'invalid'), ({'1':True},'invalid')]:
        assert check({'new_field':value},source_fields={'new_field':meta}).states['new_field'] == expected
    meta['Branching Logic (Show field only if...)'] = "__import__('os')"
    assert check({'new_field':{'1':'1'}},source_fields={'new_field':meta}).states['new_field'] == 'unverified'


def scored():
    return serialise(Scorer(C).score(CORE, epi_applicable=True))


def test_valid_exact_scores_and_explicit_unavailable_are_distinct_from_invalid():
    result = scored()
    assert validate_scores(result) == ()
    unavailable = serialise(Scorer(C).score(CORE))
    issues = validate_scores(unavailable)
    assert len(issues) == 2
    assert all(i.observed_state == 'unavailable_score' and not i.blocks_field for i in issues)
    assert result == scored()


@pytest.mark.parametrize('name', ['EPI','ESI','SBI','MHDI','BRS_100','MSPSS_100','GSE_100','PFI','NSES','K6_total'])
def test_score_specific_ranges(name):
    for value in (-1,25 if name == 'K6_total' else 101):
        result = scored();result['scores'][name]['value'] = {'numerator':value,'denominator':1}
        assert any(i.field == 'scores.'+name and i.blocks_field for i in validate_scores(result))
    if name == 'K6_total':
        result['scores'][name]['value'] = {'numerator':1,'denominator':2}
        assert any(i.observed_state == 'outside_score_range' for i in validate_scores(result))


@pytest.mark.parametrize('value', [1.0, True, '50', {'numerator':True,'denominator':1}, {'numerator':1,'denominator':0}, {'numerator':1,'denominator':-2}, {'numerator':1,'denominator':2.0}, {}, []])
def test_malformed_score_values_are_reported(value):
    result = scored();result['scores']['NSES']['value'] = value
    assert any(i.blocks_field for i in validate_scores(result))


def test_missing_result_and_conflicting_availability_or_reason():
    result = scored();result['scores'].pop('K6_total')
    assert any(i.field == 'scores.K6_total' and i.blocks_field for i in validate_scores(result))
    result = scored();result['scores']['EPI'] = {'value':None,'issues':[{'field':'EPI','state':'applicability_unverified'}]}
    assert any(i.observed_state == 'unavailable_dependency' for i in validate_scores(result))
    result['scores']['EPI']['issues'] = []
    assert any(i.observed_state == 'unexplained_unavailable' for i in validate_scores(result))
    result['scores']['EPI']['issues'] = [{'field':'EPI','state':[]}]
    assert any(i.blocks_field for i in validate_scores(result))
    for root in (None, [], {'scores':None}, {'scores':{1:None}}):
        assert any(i.blocks_field for i in validate_scores(root))


def test_repository_quality_review_retains_invalid_raw_and_rejects_bad_score_envelope(setup):
    repo,policy,identity = setup
    data = base() | {'age_years':'25','k6_1':'99','screen_form_complete':'2','extra':'retained'}
    sid = repo.ingest(identity,data,'synthetic-validation-v1')
    assert repo.export(identity,'reviewer','Ghana')['payload'] == data
    summary = repo.review(identity,'reviewer','Ghana')
    assert summary['quality']['age_eligible'] is False
    assert summary['quality']['issue_counts']['V11'] == 1
    assert 'retained' not in str(summary) and 'age_years' not in str(summary['quality'])
    with repo.engine.connect() as conn:
        layer = conn.execute(select(validated).where(validated.c.source_id == sid)).mappings().one()
        assert layer['issues']['k6_1'] == 'invalid_code'
        assert 'k6_1' not in layer['values']
    bad = scored();bad['scores']['K6_total']['value'] = {'numerator':25,'denominator':1}
    with pytest.raises(ValueError,match='Invalid V3.1 scoring result'):
        repo.store_derived(sid,'bad-range',bad)
    assert count(repo,derived) == 0


@pytest.mark.parametrize('decision', [None,False,'approved',1])
def test_quality_validation_never_bypasses_current_action_policy(setup, decision):
    repo,policy,identity = setup
    sid = repo.ingest(identity,base() | {'age_years':'12'},'synthetic-v1')
    policy.allowed = decision
    with pytest.raises(AccessDenied):
        repo.review(identity,'reviewer','Ghana')
    with pytest.raises(AccessDenied):
        repo.store_derived(sid,'synthetic-calc',scored())


def test_bad_age_or_completion_does_not_discard_independent_partial_receipt(env):
    e,policy,repo,transport,workflow,identity = env
    from etl.intake.v31 import raw as intake_raw
    transport.rows = [row() | {'age_years':'11','screen_form_complete':'0'}]
    assert workflow.sync(source_version='synthetic-validation-v1')['processed'] == 1
    assert count(repo,intake_raw) == 1
    assert repo.export(identity,'reviewer','Ghana')['payload']['age_years'] == '11'
    assert repo.review(identity,'reviewer','Ghana')['quality']['age_eligible'] is False
    assert count(repo,derived) == 1


def test_inapplicable_branch_predicates_cannot_activate_a_dependent_question():
    meta = copy.deepcopy(C['fields'][0]['dictionary_metadata'])
    meta.update({'Field Type':'radio', 'Choices, Calculations, OR Slider Labels':'0, No | 1, Yes'})
    fields = {'child':dict(meta, **{'Branching Logic (Show field only if...)':"[parent] = '1'"}),
              'parent':dict(meta, **{'Branching Logic (Show field only if...)':"[gate] = '1'"}),
              'gate':meta}
    data = {'child':'1','parent':'1','gate':'0'}
    result = check(data, source_fields=fields)
    assert result.states['parent'] == 'not_applicable'
    assert result.states['child'] == 'unverified'
    assert result.values == {'gate':'0'}
    reverse = check(data, source_fields=dict(reversed(list(fields.items()))))
    assert reverse.states == result.states
    assert reverse.values == result.values
