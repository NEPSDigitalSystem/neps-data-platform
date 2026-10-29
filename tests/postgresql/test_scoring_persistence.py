"""Independent golden expectations through a synthetic PostgreSQL workflow.

All source/NDS grants below are test-only injected decisions. Native transport
is mocked. Explicit semantic reasons have a separate persistence-only check.
"""
import json
import os
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import select

from etl.config import Settings
from etl.extract.production_client import ProductionRedcapClient
from etl.intake.v31 import Intake, raw as intake_raw, pending
from etl.repository.integrity import storage_snapshot
from etl.repository.participant_links import ParticipantLinks
from etl.repository.v31 import Repository, RecordIdentity, RegistryDecision, raw, derived, validated, audit
from etl.scoring.v31 import Scorer
from etl.sync.v31_workflow import Workflow, DownstreamProcessor, serialise
from test_v31_workflow import C, Transport

GOLDEN = json.loads((Path(__file__).parents[1] / 'fixtures/SCORING_GOLDEN.json').read_text(encoding='utf-8'))['cases']
PROJECT = 'L08-SYNTHETIC-GOLDEN'


class SyntheticPolicy:
    def resolve(self, identity):
        return RegistryDecision('Ghana', True, True, 'NDS-' + identity.participant)

    def permits(self, *args):
        return True

    def transfer_permitted(self, *args):
        return True


def check_expected(case, result, payload):
    for name, expected in case['expected'].items():
        if name == 'affected_state':
            assert expected in {i['state'] for s in result['scores'].values() for i in s['issues']}
        elif name == 'baseline_questionnaire_complete':
            assert (set(C['question_fields']) <= payload.keys()) is expected
        else:
            value = result['scores'][name]['value']
            if expected is None:
                assert value is None
            else:
                assert value is not None
                assert float(Fraction(value['numerator'], value['denominator'])) == pytest.approx(expected, rel=0, abs=1e-12)


def save_evidence(name, value):
    recovery = os.environ.get('NEPS_DE03_RECOVERY_EVIDENCE')
    if recovery:
        Path(recovery).with_name(name).write_text(json.dumps(value, indent=2) + '\n')


def test_native_golden_workflow_persistence_replay_and_correction(pg_database):
    db = pg_database
    db['migrate']()
    engine = db['engine']()
    repository = Repository(engine, SyntheticPolicy(), storage_destination='Ghana')
    intake = Intake(engine, project=PROJECT, destination='Ghana', service_identity='synthetic-collector',
                    policy=SimpleNamespace(authorises=lambda scope: True))
    links = ParticipantLinks(engine, authoriser=lambda *args: True)
    cases = [c for c in GOLDEN if c['responses'] is not None and not c.get('missingness')]
    assert len(cases) == 20
    transport = Transport()
    for case in cases:
        source_id = case['id']
        links.bind(PROJECT, source_id, 'NDS-' + source_id, 'synthetic-map-v1', 'fixture')
        transport.rows.append(dict(case['responses'], study_id=source_id, country='1', redcap_event_name='baseline'))
    original_rows = json.loads(json.dumps(transport.rows))
    settings = Settings(REDCAP_MOCK_ENABLED=False, REDCAP_API_TOKEN='synthetic-token-only',
                        REDCAP_API_URL='https://synthetic.invalid/api/', REDCAP_PROJECT_ID=PROJECT)
    client = ProductionRedcapClient(settings, session=transport, authorisation_provider=lambda scope: True, contract=C)
    collector = Workflow(client, intake, project=PROJECT, context_provider=lambda row: ('baseline', '', ''))
    processor = DownstreamProcessor(intake, repository, links, applicability_provider=lambda identity: True)
    assert collector.sync(source_version='synthetic-golden-v1')['received'] == 20
    with engine.connect() as connection:
        assert connection.execute(select(raw)).first() is None
    assert processor.process() == {'processed': 20, 'deferred': 0}
    assert transport.rows == original_rows
    with engine.connect() as connection:
        sources = connection.execute(select(raw)).mappings().all()
        assert len(sources) == 20
        receipts = {r['id']: r for r in connection.execute(select(intake_raw)).mappings()}
        for source in sources:
            case = next(c for c in cases if c['id'] == source['identity']['participant'])
            payload = next(r for r in original_rows if r['study_id'] == case['id'])
            assert source['payload'] == payload == receipts[source['intake_revision_id']]['payload']
            result = connection.execute(select(derived.c.result).where(derived.c.source_id == source['id'])).scalar_one()
            check_expected(case, result, payload)
            assert result['intake_revision_id'] == source['intake_revision_id']
            assert result['source_metadata_sha256'] == receipts[source['intake_revision_id']]['metadata_hash']
            assert result['contract_sha256'] == source['contract_hash']
            assert result['nds_participant_id'] == source['nds_participant_id'] == 'NDS-' + case['id']
            assert result['mapping_version'] == 'synthetic-map-v1'
            assert result['metadata_policy_version'] == 'local-reviewed-metadata'
            assert len(result['source_sha256']) == 64
            assert connection.execute(select(validated.c.source_id).where(validated.c.source_id == source['id'])).scalar_one() == source['id']
            assert set(connection.execute(select(audit.c.action).where(audit.c.source_id == source['id'])).scalars()) == {'ingest', 'derive'}
        assert set(connection.execute(select(pending.c.state)).scalars()) == {'acknowledged'}
    before = storage_snapshot(engine, 'neps_source')
    collector.sync(source_version='synthetic-golden-v1')
    assert processor.process() == {'processed': 0, 'deferred': 0}
    assert storage_snapshot(engine, 'neps_source') == before
    next(r for r in transport.rows if r['study_id'] == 'minimum_nses')['k6_1'] = '4'
    collector.sync(source_version='synthetic-golden-v1')
    assert processor.process() == {'processed': 1, 'deferred': 0}
    with engine.connect() as connection:
        corrected = connection.execute(select(raw).where(raw.c.identity['participant'].as_string() == 'minimum_nses').order_by(raw.c.revision)).mappings().all()
        assert [r['payload']['k6_1'] for r in corrected] == ['0', '4']
        values = [connection.execute(select(derived.c.result).where(derived.c.source_id == r['id'])).scalar_one()['scores']['NSES']['value'] for r in corrected]
        assert values == [{'numerator': 0, 'denominator': 1}, {'numerator': 10, 'denominator': 3}]
    after = storage_snapshot(engine, 'neps_source')
    assert after['nds_v31_source']['count'] == after['nds_v31_derived']['count'] == after['nds_v31_intake_raw']['count'] == 21
    save_evidence('golden-native.json', dict(native_golden_cases=[c['id'] for c in cases], all_expected_outputs_match=True,
        raw_and_provenance_links_match=True, unchanged_replay_snapshot=before, correction_snapshot=after,
        correction_nses=[{'numerator': 0, 'denominator': 1}, {'numerator': 10, 'denominator': 3}],
        component_only_case='composite_52_5 remains an ordinary arithmetic test, not a native response row'))


def test_explicit_semantic_golden_envelopes_survive_postgresql(pg_database):
    db = pg_database
    db['migrate']()
    engine = db['engine']()
    repository = Repository(engine, SyntheticPolicy(), storage_destination='Ghana')
    scorer = Scorer(C)
    cases = [c for c in GOLDEN if c.get('missingness')]
    assert len(cases) == 3
    for case in cases:
        identity = RecordIdentity(PROJECT, case['id'], 'baseline', '', '')
        payload = dict(case['responses'], study_id=case['id'], country='1')
        source_id = repository.ingest(identity, payload, 'synthetic-semantic-v1', 'fixture')
        scored = scorer.score(case['responses'], missingness=case['missingness'], epi_applicable=True,
                              source_context={'source_id': source_id, 'purpose': 'synthetic-explicit-reason-persistence'})
        result = serialise(scored)
        repository.store_derived(source_id, scored.algorithm_version + ':' + scored.source_sha256, result, 'fixture')
        with engine.connect() as connection:
            stored = connection.execute(select(derived.c.result).where(derived.c.source_id == source_id)).scalar_one()
            assert stored == result
            assert connection.execute(select(raw.c.payload).where(raw.c.id == source_id)).scalar_one() == payload
            check_expected(case, stored, payload)
            assert set(connection.execute(select(audit.c.action).where(audit.c.source_id == source_id)).scalars()) == {'ingest', 'derive'}
    save_evidence('golden-semantic.json', dict(cases=[c['id'] for c in cases], expected_outputs_and_reasons_match=True,
        scope='Explicit test-only semantic reasons through scorer, repository and PostgreSQL. Not inferred by native collector.'))
