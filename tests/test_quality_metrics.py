"""Independent worked examples for local reporting conventions."""
import copy
from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path

import pytest

from etl.analytics.quality_metrics import rate, quality_summary, moments, correlation, composite_check


def test_count_ratios_and_zero_denominator():
    assert rate(3, 4) == Fraction(3, 4)
    assert rate(0, 4) == 0
    assert rate(0, 0) is None
    with pytest.raises(ValueError):
        rate(5, 4)


def test_mean_median_and_sample_standard_deviation():
    actual = moments([10, None, 20, 30])
    assert actual == {'n': 3, 'mean': 20, 'median': 20, 'sample_sd': Decimal(10)}
    assert moments([10, 30])['sample_sd'] == Decimal(200).sqrt()
    assert moments([Fraction(1, 3), Fraction(2, 3)])['mean'] == Fraction(1, 2)
    assert moments([4]) == {'n': 1, 'mean': 4, 'median': 4, 'sample_sd': None}
    assert moments([None]) == {'n': 0, 'mean': None, 'median': None, 'sample_sd': None}


@pytest.mark.parametrize('value', [True, 0.1, '10'])
def test_reporting_math_rejects_implicit_numeric_conversion(value):
    with pytest.raises(ValueError):
        moments([value])


def test_pairwise_complete_correlation_and_constant_cases():
    assert correlation([(1, 2), (2, 4), (3, None), (None, 7)]) == {'n': 2, 'r': 1, 'reason': None}
    assert correlation([(1, 4), (2, 2)])['r'] == -1
    assert correlation([(1, 4), (1, 2)]) == {'n': 2, 'r': None, 'reason': 'constant_input'}
    assert correlation([(1, None), (2, 3)]) == {'n': 1, 'r': None, 'reason': 'insufficient_pairs'}


def test_independent_composite_arithmetic_and_unavailable_components():
    inputs = dict(EPI=20, ESI=40, SBI=60, MHDI=80, PFI=100)
    assert composite_check(inputs, 44) == {'expected': 44, 'matches': True, 'reason': None}
    assert composite_check(inputs, 45)['matches'] is False
    assert composite_check(inputs | {'EPI': None}, None)['matches'] is True
    assert composite_check(inputs | {'EPI': None}, 0)['matches'] is False
    with pytest.raises(ValueError):
        composite_check(inputs | {'PFI': 101}, 44)


def test_quality_denominators_keep_missingness_and_branch_uncertainty_separate():
    root = Path(__file__).parents[1]
    contract = json.loads((root/'etl/contracts/data_contract_v31.json').read_text(encoding='utf-8'))
    payload = {'study_id': 'SYNTHETIC-QUALITY', 'willing_24m': '99', 'k6_1': '0', 'k6_2': '99'}
    before = copy.deepcopy(payload)
    result = quality_summary(payload, contract)
    assert payload == before
    assert result['expected_questions'] == 188
    assert result['recorded'] == 3
    assert result['recorded_completeness'] == Fraction(3, 188)
    assert result['question_states']['refused'] == 1
    assert result['question_states']['invalid'] == 1
    assert result['coded_attempts'] == 3 and result['declared_codes'] == 2
    assert result['coding_consistency'] == Fraction(2, 3)
    assert result['valid'] == result['invalid'] == 1
    assert result['validity'] == Fraction(1, 2)
    assert result['applicable'] + result['excluded'] + result['applicability_unverified'] == 188


def test_branch_inapplicability_is_not_counted_as_missing_or_invalid():
    root = Path(__file__).parents[1]
    contract = json.loads((root/'etl/contracts/data_contract_v31.json').read_text(encoding='utf-8'))
    absent = quality_summary({}, contract)
    known = quality_summary({'currently_school': '0'}, contract)
    assert known['excluded'] > absent['excluded']
    assert known['applicability_unverified'] < absent['applicability_unverified']


def test_numeric_validity_includes_administrative_age_without_inflating_question_counts():
    root = Path(__file__).parents[1]
    contract = json.loads((root/'etl/contracts/data_contract_v31.json').read_text(encoding='utf-8'))
    good = quality_summary({'age_years':'12'}, contract)
    bad = quality_summary({'age_years':'25'}, contract)
    assert good['numeric_date_valid']==1 and good['numeric_date_invalid']==0
    assert good['numeric_date_validity']==1 and good['recorded']==0
    assert bad['numeric_date_valid']==0 and bad['numeric_date_invalid']==1
    assert bad['numeric_date_validity']==0 and bad['recorded']==0
