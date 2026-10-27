"""Independent synthetic repository fixtures; no source participant data."""
import json
from pathlib import Path
from dataclasses import replace

import pytest
from sqlalchemy import create_engine, select, func, inspect, event
from etl.repository.v31 import (Repository, RecordIdentity, RegistryDecision, AccessDenied,
                               raw, validated, derived, audit, branch_state)
from etl.repository.migration import upgrade, downgrade


class TrustedSyntheticPolicy:
    def __init__(self):
        self.state = RegistryDecision('Ghana', True, True)
        self.allowed, self.transfer = True, True
    def resolve(self, identity):
        return self.state
    def permits(self, identity, action, actor, destination):
        return self.allowed
    def transfer_permitted(self, identity, destination):
        return self.transfer


@pytest.fixture
def setup():
    engine = create_engine('sqlite:///:memory:')
    @event.listens_for(engine, 'connect')
    def enable_foreign_keys(dbapi_connection, connection_record):
        dbapi_connection.execute('PRAGMA foreign_keys=ON')
    with engine.begin() as conn:
        upgrade(conn)
    policy = TrustedSyntheticPolicy()
    return Repository(engine, policy, storage_destination='Ghana'), policy, RecordIdentity('synthetic-project', 'SYN-1', 'baseline', '', '')


def base():
    return {'study_id': 'SYN-1', 'country': '1'}


def count(repo, table):
    with repo.engine.connect() as conn:
        return conn.execute(select(func.count()).select_from(table)).scalar_one()


def test_all_188_lossless_and_missingness(setup):
    repo, policy, identity = setup
    payload = base()
    for i, name in enumerate(repo.contract['question_fields']):
        # Distinct synthetic representations: empty, null, literal code, absent.
        if i % 4 != 3:
            payload[name] = ['', None, '98'][i % 4]
    payload['bully_type'] = {'1': '1', '2': '0'}
    sid = repo.ingest(identity, payload, 'synthetic-v1')
    out = repo.export(identity, 'synthetic-researcher', 'Ghana')
    assert out['payload'] == payload
    assert out['contract_hash'] == repo.contract_hash
    assert len(repo.contract['question_fields']) == 188
    assert all((name in out['payload']) == (name in payload) for name in repo.contract['question_fields'])
    with repo.engine.connect() as conn:
        layer = conn.execute(select(validated).where(validated.c.source_id == sid)).mappings().one()
        assert '98' in payload.values()
        assert 'source_only_administrative_or_derived' == layer['issues']['study_id']


def test_all_188_nonempty_full_roundtrip(setup):
    repo, _, identity = setup
    payload = base() | {name: '99' for name in repo.contract['question_fields']}
    repo.ingest(identity, payload, 'synthetic-v1')
    assert repo.export(identity, 'researcher', 'Ghana')['payload'] == payload
    assert len(set(payload) & set(repo.contract['question_fields'])) == 188


def test_partial_corrections_replay_reversion_and_identity(setup):
    repo, _, identity = setup
    a = base() | {'k6_1': '1'}
    first = repo.ingest(identity, a, 'v1')
    assert repo.ingest(identity, a, 'v1') == first
    second = repo.ingest(identity, base() | {'k6_1': ''}, 'v1')
    assert first != second
    third = repo.ingest(identity, a, 'v1')
    assert third not in (first, second)
    for new in [replace(identity, project='other'), replace(identity, event='month_6'),
                replace(identity, instrument='neps31_yeb', instance='1'),
                replace(identity, instrument='neps31_yeb', instance='2')]:
        assert repo.ingest(new, a, 'v1') not in (first, second, third)
    assert count(repo, raw) == 7
    assert count(repo, audit) == 8


@pytest.mark.parametrize('failure', ['absent', 'withdrawn', 'processing', 'role', 'country', 'linkage'])
def test_deny_ingest_without_trusted_current_state(setup, failure):
    repo, policy, identity = setup
    payload = base()
    if failure == 'absent': repo.adapter = None
    if failure == 'withdrawn': policy.state = replace(policy.state, consent_current=False)
    if failure == 'processing': policy.state = replace(policy.state, processing_allowed=False)
    if failure == 'role': policy.allowed = False
    if failure == 'country': payload['country'] = '2'
    if failure == 'linkage': payload['study_id'] = 'SYN-OTHER'
    with pytest.raises(AccessDenied): repo.ingest(identity, payload, 'v1')
    assert count(repo, raw) == 0


def test_export_rechecks_consent_transfer_and_country(setup):
    repo, policy, identity = setup
    repo.ingest(identity, base(), 'v1')
    policy.transfer = False
    with pytest.raises(AccessDenied): repo.export(identity, 'researcher', 'Tanzania')
    policy.transfer = True
    policy.state = replace(policy.state, consent_current=False)
    with pytest.raises(AccessDenied): repo.export(identity, 'researcher', 'Ghana')
    policy.state = RegistryDecision('Tanzania', True, True)
    with pytest.raises(AccessDenied): repo.export(identity, 'researcher', 'Ghana')
    assert count(repo, audit) == 1


def test_validation_branching_and_codes_keep_raw(setup):
    repo, _, identity = setup
    payload = base() | {'currently_school': '0', 'epix_exams_1': '1', 'k6_1': 'bogus',
                        'sbi_exper_1': '1', 'nses': '123', 'invented': '99'}
    sid = repo.ingest(identity, payload, 'v1')
    assert repo.export(identity, 'researcher', 'Ghana')['payload'] == payload
    with repo.engine.connect() as conn:
        row = conn.execute(select(validated).where(validated.c.source_id == sid)).mappings().one()
        assert row['issues']['epix_exams_1'] == 'inapplicable'
        assert row['issues']['sbi_exper_1'] == 'branch_unverified'
        assert row['issues']['k6_1'] == 'invalid_code'
        assert row['issues']['invented'] == 'unknown_field'
        assert 'nses' not in row['values']
    assert branch_state("[x] = '1' and ([y] = '2' or [z] = '3')", {'x':'1','z':'3'}) is True
    assert branch_state("__import__('os')", {}) is None


def test_derived_versions_and_upstream_stale_rejection(setup):
    repo, _, identity = setup
    first = repo.ingest(identity, base(), 'v1')
    did = repo.store_derived(first, 'synthetic-calculation-v1', {'status': 'incomplete'})
    assert repo.store_derived(first, 'synthetic-calculation-v1', {'status': 'incomplete'}) == did
    with pytest.raises(ValueError): repo.store_derived(first, 'synthetic-calculation-v1', {'status': 'changed'})
    repo.store_derived(first, 'synthetic-calculation-v2', {'status': 'incomplete'})
    second = repo.ingest(identity, base() | {'k6_1':'2'}, 'v1')
    with pytest.raises(ValueError): repo.store_derived(first, 'v3', {})
    repo.store_derived(second, 'synthetic-calculation-v2', {'status': 'incomplete'})
    assert count(repo, derived) == 3


def test_transaction_rollback_on_audit_failure(setup, monkeypatch):
    repo, _, identity = setup
    def fail(*args): raise RuntimeError('synthetic audit failure')
    monkeypatch.setattr(repo, '_audit', fail)
    with pytest.raises(RuntimeError): repo.ingest(identity, base(), 'v1')
    assert count(repo, raw) == count(repo, validated) == count(repo, audit) == 0


def test_additive_schema_rollback_disposable_only(setup):
    repo, _, _ = setup
    with repo.engine.begin() as conn:
        with pytest.raises(PermissionError): downgrade(conn)
        downgrade(conn, disposable_synthetic_database=True)
        assert inspect(conn).get_table_names() == []
        upgrade(conn)
        assert len(inspect(conn).get_table_names()) == 4


@pytest.mark.parametrize('destination', [None, '', 1])
def test_destination_required(setup, destination):
    repo, _, identity = setup
    repo.ingest(identity, base(), 'v1')
    with pytest.raises(AccessDenied): repo.export(identity, 'researcher', destination)


def test_all_supplied_branch_expressions_are_supported(setup):
    repo, _, _ = setup
    all_false = {name: 'synthetic-nonmatching-code' for name in repo.fields}
    for field in repo.fields.values():
        expression = field['Branching Logic (Show field only if...)']
        if expression:
            assert branch_state(expression, all_false) is False


def test_derived_rechecks_current_registry_country(setup):
    repo, policy, identity = setup
    sid = repo.ingest(identity, base(), 'v1')
    policy.state = RegistryDecision('Tanzania', True, True)
    with pytest.raises(AccessDenied): repo.store_derived(sid, 'v1', {})


@pytest.mark.parametrize('field', ['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'])
def test_source_event_repeat_mismatch_denied(setup, field):
    repo, _, identity = setup
    with pytest.raises(AccessDenied): repo.ingest(identity, base() | {field: 'mismatch'}, 'v1')
    assert count(repo, raw) == 0


@pytest.mark.parametrize('instance', [True, 1.0, 0, -1, '2'])
def test_repeat_identity_comparison_rejects_other_native_values(setup, instance):
    from dataclasses import replace
    repo, _, identity = setup
    repeated = replace(identity, instrument='neps31_yeb', instance='1')
    payload = base() | {'redcap_repeat_instrument': 'neps31_yeb',
                        'redcap_repeat_instance': instance}
    with pytest.raises(AccessDenied):
        repo.ingest(repeated, payload, 'synthetic-v1')
    assert count(repo, raw) == 0


def test_storage_destination_and_current_grant_required(setup):
    repo, policy, identity = setup
    policy.transfer = False
    with pytest.raises(AccessDenied): repo.ingest(identity, base(), 'v1')
    policy.transfer = True
    sid = repo.ingest(identity, base(), 'v1')
    policy.transfer = False
    with pytest.raises(AccessDenied): repo.store_derived(sid, 'v1', {})
    policy.transfer = True
    repo.storage_destination = None
    with pytest.raises(AccessDenied): repo.ingest(identity, base(), 'v1')
    with pytest.raises(AccessDenied): repo.store_derived(sid, 'v1', {})


def test_sqlite_foreign_keys_enabled(setup):
    repo, _, _ = setup
    with repo.engine.connect() as conn:
        assert conn.exec_driver_sql('PRAGMA foreign_keys').scalar() == 1


def test_source_defined_text_count_validation_without_invented_upper_bound(setup):
    repo, _, identity = setup
    payload = base() | {'household_language':'Synthetic test language', 'household_members':'0',
                        'asset_sleeprooms':'-1', 'attack_12m':'2', 'attack_freq_missing':'1',
                        'attack_freq':'1000000'}
    sid = repo.ingest(identity, payload, 'v1')
    with repo.engine.connect() as c:
        layer = c.execute(select(validated).where(validated.c.source_id == sid)).mappings().one()
        assert layer['values']['household_language'] == payload['household_language']
        assert layer['values']['household_members'] == '0'
        assert layer['values']['attack_freq'] == '1000000'
        assert layer['issues']['asset_sleeprooms'] == 'outside_dictionary_range'
    assert repo.export(identity, 'researcher', 'Ghana')['payload'] == payload
