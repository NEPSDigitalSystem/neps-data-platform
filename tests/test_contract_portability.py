"""Reference integrity and contract stability across checkout locations."""
import hashlib
import json
from pathlib import Path
import shutil

from etl.contracts.v31 import build_from_sources

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / 'tests/fixtures/v31_reference'


def test_reference_and_independent_golden_bytes_match_handover():
    for item in json.loads((ROOT / 'tests/fixtures/v31_sources.json').read_text()):
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']


def test_contract_regeneration_does_not_depend_on_checkout_location(tmp_path):
    moved = tmp_path / 'another checkout' / 'references'
    shutil.copytree(REFERENCES, moved)
    actual = build_from_sources(moved)
    expected = json.loads((ROOT / 'etl/contracts/data_contract_v31.json').read_text(encoding='utf-8'))
    assert actual == expected
    assert all(not Path(item['path']).is_absolute() for item in actual['sources'])
