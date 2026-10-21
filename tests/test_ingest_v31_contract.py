"""The packaged V3.1 contract must resolve from any checkout location.

ingest-v31 reads the contract before it touches the source or the database, so a
wrong package-relative path fails the whole command with an error that looks like
a source outage. These checks keep the packaging bug visible in the normal suite.
"""
from pathlib import Path

from etl.ingest_v31_simple import CONTRACT_PATH, load_v31_contract

REPO = Path(__file__).resolve().parents[1]


def test_packaged_contract_path_resolves_inside_the_package():
    assert CONTRACT_PATH.exists(), f'V3.1 contract not found at {CONTRACT_PATH}'
    assert CONTRACT_PATH.parents[1] == REPO / 'etl'


def test_ingest_v31_loads_the_packaged_contract():
    contract = load_v31_contract()
    assert contract['contract_version']
    assert len(contract['core_73_fields']) == 73
