"""Golden expectations authored independently by QA without scorer imports."""
import copy
import json
from pathlib import Path
import unittest
from etl.scoring.v31 import Scorer, composite
ROOT = Path(__file__).resolve().parent / 'fixtures'
CONTRACT = Path(__file__).resolve().parents[1] / 'etl/contracts/data_contract_v31.json'

class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.scorer = Scorer(cls.contract)
        cls.cases = json.loads((ROOT / 'SCORING_GOLDEN.json').read_text(encoding="utf-8"))['cases']
        cls.base = next(c['responses'] for c in cls.cases if c['id'] == 'minimum_nses')

    def test_independent_golden_cases(self):
        for case in self.cases:
            with self.subTest(case=case['id']):
                if case['responses'] is None:
                    c = case['component_inputs']
                    self.assertEqual(float(composite(*(c[n] for n in ('EPI','ESI','SBI','MHDI','PFI')))), case['expected']['NSES'])
                    continue
                result = self.scorer.score(case['responses'], epi_applicable=True, missingness=case.get('missingness'))
                for name, expected in case['expected'].items():
                    if name == 'affected_state':
                        self.assertIn(expected, [i.state for s in result.scores.values() for i in s.issues])
                    elif name == 'baseline_questionnaire_complete':
                        self.assertFalse(set(self.contract['question_fields']) <= case['responses'].keys())
                    elif expected is None:
                        self.assertIsNone(result.scores[name].value)
                    else:
                        self.assertAlmostEqual(float(result.scores[name].value), expected, places=12)

    def test_each_core_item_required_for_affected_score(self):
        for name in self.contract['core_73_fields']:
            with self.subTest(field=name):
                result = self.scorer.score({n:v for n,v in self.base.items() if n != name}, epi_applicable=True)
                self.assertIsNone(result.scores['NSES'].value)
                self.assertIn(name, [i.field for i in result.scores['NSES'].issues])

    def test_applicability_fail_closed(self):
        result = self.scorer.score(self.base)
        self.assertIsNone(result.scores['EPI'].value)
        self.assertIsNone(result.scores['NSES'].value)
        self.assertEqual(result.scores['EPI'].issues[-1].state, 'applicability_unverified')
        self.assertIsNotNone(result.scores['ESI'].value)

    def test_source_change_recalculates_and_hashes_without_mutation(self):
        base = copy.deepcopy(self.base)
        original = copy.deepcopy(base)
        first = self.scorer.score(base, epi_applicable=True, source_context={'event':'baseline','instance':'1'})
        self.assertEqual(base, original)
        base['k6_1'] = '4'
        second = self.scorer.score(base, epi_applicable=True, source_context={'event':'baseline','instance':'1'})
        repeated = self.scorer.score(base, epi_applicable=True, source_context={'event':'baseline','instance':'2'})
        self.assertNotEqual(first.source_sha256, second.source_sha256)
        self.assertNotEqual(second.source_sha256, repeated.source_sha256)
        self.assertNotEqual(first.scores['NSES'].value, second.scores['NSES'].value)
        self.assertEqual(first.algorithm_version, second.algorithm_version)
        self.assertEqual(self.scorer.score(base, epi_applicable=True), self.scorer.score(base, epi_applicable=True))

    def test_absence_and_explicit_null_have_distinct_provenance(self):
        absent = dict(self.base)
        name = self.contract["core_73_fields"][0]
        absent.pop(name)
        explicit_null = dict(absent, **{name: None})
        a = self.scorer.score(absent, epi_applicable=True)
        b = self.scorer.score(explicit_null, epi_applicable=True)
        self.assertNotEqual(a.source_sha256, b.source_sha256)
        self.assertEqual(a.scores, b.scores)

    def test_contract_drift_changes_version(self):
        altered = copy.deepcopy(self.contract)
        altered['contract_version'] += '-test'
        self.assertNotEqual(self.scorer.version, Scorer(altered).version)

    def test_bad_contract_rejected(self):
        for kind in ('membership','choice','direction'):
            altered = copy.deepcopy(self.contract)
            if kind == 'membership':
                altered['core_73_fields'][0] = altered['core_73_fields'][1]
            else:
                field = next(f for f in altered['fields'] if f['core_73'])
                if kind == 'choice':
                    field['dictionary_metadata']['Choices, Calculations, OR Slider Labels'] += ' | 99, Refused'
                else:
                    field['analysis_mapping']['scoring_or_direction'] = 'reverse guessed'
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                Scorer(altered)

    def test_unknown_semantics_rejected(self):
        with self.assertRaises(ValueError):
            self.scorer.score({}, missingness={'epi_expectations_1':'guess'})
        with self.assertRaises(ValueError):
            self.scorer.score({}, epi_applicable='yes')

    def test_components_bounds(self):
        for value in (-1,101):
            with self.assertRaises(ValueError): composite(value,0,0,0,0)

if __name__ == '__main__': unittest.main()
