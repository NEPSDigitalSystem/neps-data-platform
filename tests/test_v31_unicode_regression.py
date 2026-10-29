"""Reproduce the analyst's ANSI-decoding failure without requiring Windows."""
import json
from fractions import Fraction
from pathlib import Path
import runpy

import pytest

from etl.scoring.v31 import Scorer


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "etl/contracts/data_contract_v31.json"
REVERSED = {"brs_02", "brs_04", "brs_06"}


@pytest.fixture
def cp1252_default(monkeypatch):
    """Model the reported Windows default, including pathlib's 'locale' value."""
    original_open = Path.open

    def ansi_open(path, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
        if "b" not in mode and encoding in (None, "locale"):
            encoding = "cp1252"
        return original_open(path, mode, buffering, encoding, errors, newline)

    monkeypatch.setattr(Path, "open", ansi_open)


def test_implicit_ansi_decode_reproduces_reported_direction_failure(cp1252_default):
    broken = json.loads(CONTRACT.read_text())
    directions = {
        field["analysis_mapping"]["scoring_or_direction"]
        for field in broken["fields"] if field["name"] in REVERSED
    }
    assert directions == {"6\u00e2\u02c6\u2019raw"}
    with pytest.raises(ValueError, match="Unverified scoring direction"):
        Scorer(broken)


def test_explicit_utf8_preserves_minus_and_verified_reverse_membership(cp1252_default):
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    directions = {
        field["analysis_mapping"]["scoring_or_direction"]
        for field in contract["fields"] if field["name"] in REVERSED
    }
    assert directions == {"6\u2212raw"}
    assert Scorer(contract).reverse == REVERSED


@pytest.mark.parametrize("filename,class_name,check", [
    ("test_v31_scoring.py", "ScoringTests", "test_independent_golden_cases"),
    ("test_v31_scoring_qa.py", "IndependentScoringQA", "test_each_reversed_item_all_native_values"),
    ("test_v31_contract.py", "V31ContractTests", "test_regeneration_from_actual_documents_matches_saved_contract"),
    ("test_v31_contract_qa.py", "IndependentContractQA", "test_actual_exact_headers_and_raw_dictionary_equal"),
])
def test_actual_suites_load_from_other_directory_with_ansi_default(
    filename, class_name, check, cp1252_default, monkeypatch, tmp_path
):
    # Execute the existing entry points. Removing encoding from their reads must
    # fail this test even on a Linux host whose real default is UTF-8.
    suite = runpy.run_path(str(ROOT / "tests" / filename))[class_name]
    monkeypatch.chdir(tmp_path)
    suite.setUpClass()
    getattr(suite(methodName=check), check)()


@pytest.mark.parametrize("field", sorted(REVERSED))
@pytest.mark.parametrize("raw,reversed_raw", [(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)])
def test_reverse_examples_reach_actual_scorer(field, raw, reversed_raw, cp1252_default):
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    golden = json.loads((ROOT / "tests/fixtures/SCORING_GOLDEN.json").read_text(encoding="utf-8"))
    base = next(case["responses"] for case in golden["cases"] if case["id"] == "minimum_nses")
    responses = dict(base, **{field: str(raw)})
    result = Scorer(contract).score(responses, epi_applicable=True)
    # The other five items each contribute 5. Derive the expected BRS from the
    # analyst's explicit 1->5, 2->4, 3->3, 4->2, 5->1 examples, not scorer output.
    expected_brs = (Fraction(25 + reversed_raw, 6) - 1) * 25
    assert result.scores["BRS_100"].value == expected_brs
    assert result.scores["PFI"].value == (200 + expected_brs) / 3
    assert result.scores["NSES"].value == (100 - expected_brs) / 60
    assert responses[field] == str(raw)
