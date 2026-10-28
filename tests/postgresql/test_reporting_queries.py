"""L05 SQL acceptance prepared for L08's disposable PostgreSQL run.

Fixtures include deliberately malformed legacy score/raw values. Direct owner
inserts here exercise reporting, not approved ingestion or scientific rules.
"""
from dataclasses import asdict
import math

import pytest
from sqlalchemy import select, text, update
from sqlalchemy.exc import DBAPIError

from etl.analytics.query_library import run_query
from etl.repository.v31 import raw, validated, derived, RecordIdentity, digest
from etl.repository.integrity import storage_snapshot
from etl.validation.v31_validator import SCORE_NAMES

SCHEMA = 'neps_source'
PROJECT = 'L05-SYNTHETIC'
DESTINATION = 'synthetic-store'


def report(engine, name, **changes):
    scope = dict(project=PROJECT, destination=DESTINATION, country='Ghana', field='age_years',
                 algorithm_version='SYNTHETIC-ALGORITHM', metadata_policy_version='synthetic-policy',
                 expected_contract_version='synthetic-current', expected_contract_hash='current-hash',
                 dataset_class='synthetic', sample_limit=2)
    return run_query(engine, name, SCHEMA, **(scope | changes))


@pytest.fixture
def reporting_db(pg_database):
    db = pg_database;db['migrate']()
    engine = db['engine']()

    def source(sid, participant, payload, *, revision=1, event='baseline', instrument='', instance='',
               project=PROJECT, destination=DESTINATION, country='Ghana', nds=True, old=False):
        identity = asdict(RecordIdentity(project, participant, event, instrument, instance))
        with engine.begin() as connection:
            connection.execute(raw.insert().values(id=sid, identity_key=digest(identity), identity=identity,
                revision=revision, change_hash='synthetic-'+sid, source_version='fixture-v1',
                contract_version='synthetic-old' if old else 'synthetic-current',
                contract_hash='old-hash' if old else 'current-hash', payload={'study_id':participant} | payload,
                country=country, observed_at='2026-10-27T00:00:00+00:00', storage_destination=destination,
                nds_participant_id='NDS-'+participant if nds else None, intake_revision_id=None,
                source_metadata=None, source_metadata_hash=None))
            connection.execute(validated.insert().values(source_id=sid, values={},
                issues={'age_years':'outside_dictionary_range'} if sid=='d' else {}))

    def score(sid, value, *, suffix='', algorithm='SYNTHETIC-ALGORITHM', policy='synthetic-policy', malformed=False):
        scores = {name: {'value': None if value is None else
                        {'numerator':0 if name=='K6_total' else value,'denominator':1},
                        'issues':[{'field':name,'state':'missing'}] if value is None else []}
                  for name in SCORE_NAMES}
        if malformed:
            scores['EPI']['value'] = {'numerator':10, 'denominator':0}
        result = dict(algorithm_version=algorithm, metadata_policy_version=policy,
                      contract_sha256='current-hash', provisional=True, scores=scores)
        with engine.begin() as connection:
            connection.execute(derived.insert().values(id='score-'+sid+suffix, source_id=sid,
                calculation_version=algorithm+':'+sid+suffix, result=result))

    source('a-old','A',{'age_years':'12','country':'1'},old=True)
    source('a-new','A',{'age_years':'20','country':'1'},revision=2)
    source('a-repeat','A',{},event='month6',instrument='neps31_yeb',instance='1')
    source('b','B',{'age_years':None,'country':None})
    source('c','C',{'age_years':'','country':''},nds=False)
    source('d','D',{'age_years':'99','country':'9'})
    source('e','E',{'age_years':'24','country':'1'})
    source('f-old','F',{'age_years':'18','country':'1'})
    source('f-new','F',{'age_years':'19','country':'3'},revision=2,country='Tanzania')
    source('other-project','OTHER',{'age_years':'18'},project='OTHER-PROJECT')
    source('other-destination','OTHER',{'age_years':'18'},destination='other-store')
    score('a-old',100);score('a-new',10);score('b',30);score('c',None)
    score('d',40);score('d',50,suffix='-second');score('e',10,malformed=True);score('f-new',90)
    score('a-new',99,suffix='-other-algorithm',algorithm='OTHER-ALGORITHM')
    score('b',88,suffix='-other-policy',policy='other-policy')
    return engine


def test_all_six_reports_and_no_storage_changes(reporting_db):
    engine = reporting_db
    before = storage_snapshot(engine, SCHEMA)
    counts = report(engine, 'data_counts')[0]
    assert counts == dict(retained_revisions=8, latest_records=6, native_source_participants=5,
                          mapped_nds_participants=4, unmapped_latest_records=1)
    scores = report(engine, 'scoring_distribution')
    epi = next(row for row in scores if row['score_name']=='EPI')
    assert len(scores)==10
    assert {key:epi[key] for key in ('latest_records','available','unavailable','unscored','ambiguous','malformed','out_of_range')} == dict(
        latest_records=6,available=2,unavailable=1,unscored=1,ambiguous=1,malformed=1,out_of_range=0)
    assert epi['mean']==20 and epi['median']==20
    assert float(epi['sample_sd']) == pytest.approx(math.sqrt(200))
    assert epi['minimum']==10 and epi['maximum']==30
    nulls = report(engine,'null_analysis')
    raw_counts = {state:sum(row['records'] for row in nulls if row['raw_state']==state)
                  for state in ('absent','json_null','empty','present')}
    assert raw_counts==dict(absent=1,json_null=1,empty=1,present=3)
    assert sum(row['records'] for row in nulls if row['validation_issue']=='outside_dictionary_range')==1
    countries = report(engine,'country_distribution')
    assert {row['raw_country_code']:row['latest_records'] for row in countries} == {
        '1':2,'ABSENT':1,'JSON_NULL':1,'EMPTY':1,'UNMAPPED':1}
    assert sum(row['latest_records'] for row in countries if row['country_consistency']=='unmapped')==1
    versions = report(engine,'contract_version_check')
    assert {(row['contract_version'],row['retained_revisions'],row['latest_records'],row['matches_expected_contract'])
            for row in versions} == {('synthetic-old',1,0,False),('synthetic-current',7,6,True)}
    samples = report(engine,'sample_records')
    assert len(samples)==2 and [row['sample_ordinal'] for row in samples]==[1,2]
    assert set(samples[0])=={'sample_ordinal','revision','contract_version','contract_hash','payload_key_count',
                            'metadata_hash_present','intake_link_present','nds_mapping_present'}
    assert storage_snapshot(engine, SCHEMA)==before


def test_project_destination_country_and_repeat_scope(reporting_db):
    engine = reporting_db
    assert report(engine,'data_counts',country=None)[0]['latest_records']==7
    assert report(engine,'data_counts',country='Tanzania')[0]['latest_records']==1
    assert report(engine,'data_counts',destination='other-store')[0]['latest_records']==1
    assert report(engine,'data_counts',project='OTHER-PROJECT')[0]['latest_records']==1
    assert report(engine,'data_counts',event='baseline')[0]['latest_records']==5
    assert report(engine,'data_counts',event='month6',instrument='neps31_yeb',instance='1')[0]['latest_records']==1
    assert report(engine,'data_counts',event='')[0]['latest_records']==0
    assert report(engine,'data_counts',project="x' OR true --")[0]['latest_records']==0
    nulls=report(engine,'null_analysis',field="x' OR true --")
    assert len(nulls)==1 and nulls[0]['raw_state']=='absent' and nulls[0]['records']==6


def test_bad_score_ranges_and_single_observation_statistics(reporting_db):
    engine=reporting_db
    with engine.begin() as connection:
        result=connection.execute(select(derived.c.result).where(derived.c.id=='score-e')).scalar_one()
        result['scores']['EPI']['value']={'numerator':101,'denominator':1}
        connection.execute(update(derived).where(derived.c.id=='score-e').values(result=result))
        result=connection.execute(select(derived.c.result).where(derived.c.id=='score-b')).scalar_one()
        result['scores']['EPI']['value']={'numerator':1,'denominator':-1}
        connection.execute(update(derived).where(derived.c.id=='score-b').values(result=result))
    epi=next(row for row in report(engine,'scoring_distribution') if row['score_name']=='EPI')
    assert epi['out_of_range']==1 and epi['malformed']==1 and epi['available']==1
    assert epi['mean']==10 and epi['median']==10 and epi['sample_sd'] is None


def test_empty_reporting_scope(reporting_db):
    engine=reporting_db
    counts=report(engine,'data_counts',project='EMPTY')[0]
    assert set(counts.values())=={0}
    for name in ('scoring_distribution','null_analysis','country_distribution','contract_version_check','sample_records'):
        assert report(engine,name,project='EMPTY')==[]


def test_other_metadata_policy_does_not_mix_candidates(reporting_db):
    rows=report(reporting_db,'scoring_distribution',metadata_policy_version='other-policy')
    epi=next(row for row in rows if row['score_name']=='EPI')
    assert epi['available']==1 and epi['mean']==88 and epi['unscored']==5
    assert epi['ambiguous']==0


def test_read_only_transaction_rejects_writes(reporting_db,monkeypatch):
    from etl.analytics import query_library
    before=storage_snapshot(reporting_db,SCHEMA)
    monkeypatch.setattr(query_library,'prepare_query',lambda *a,**kw:(
        text('DELETE FROM neps_source.nds_v31_source'),{}))
    with pytest.raises(DBAPIError):
        report(reporting_db,'data_counts')
    assert storage_snapshot(reporting_db,SCHEMA)==before
