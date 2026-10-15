"""Independent scorer safety checks outside implementation-authored suite."""
import copy,json
from pathlib import Path
from fractions import Fraction
import unittest
from etl.scoring.v31 import Scorer
ROOT=Path(__file__).resolve().parents[1]
class IndependentScoringQA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.contract=json.loads((ROOT/'etl/contracts/data_contract_v31.json').read_text())
  cls.scorer=Scorer(cls.contract)
  gold=json.loads((ROOT.parents[1]/'.codex-build/SCORING_GOLDEN.json').read_text())
  cls.base=next(c['responses'] for c in gold['cases'] if c['id']=='minimum_nses')
 def test_true_economic_zero_is_valid(self):
  r=self.scorer.score(self.base,epi_applicable=True)
  self.assertEqual(r.scores['ESI'].value,Fraction(0))
  self.assertEqual(r.scores['K6_total'].value,Fraction(0))
  self.assertEqual(r.scores['NSES'].value,Fraction(0))
 def test_refusal_unknown_na_are_distinct_versioned_reasons(self):
  hashes=set()
  for state in ['refused','unknown','not_applicable']:
   result=self.scorer.score(self.base,epi_applicable=True,missingness={'epi_expectations_1':state})
   self.assertIsNone(result.scores['EPI'].value)
   self.assertIsNone(result.scores['NSES'].value)
   self.assertEqual(result.scores['EPI'].issues[0].state,state)
   hashes.add(result.source_sha256)
  self.assertEqual(len(hashes),3)
 def test_all_reversed_items_missing_never_convert_to_numeric(self):
  for name in ['brs_02','brs_04','brs_06']:
   source=dict(self.base);source[name]=''
   result=self.scorer.score(source,epi_applicable=True)
   self.assertIsNone(result.scores['BRS_100'].value)
   self.assertIsNone(result.scores['PFI'].value)
   self.assertIsNone(result.scores['NSES'].value)
 def test_non_native_source_values_are_rejected_without_normalising(self):
  for raw in [True,1.0,' 1','1 ','01','1.0']:
   source=dict(self.base);source['epi_expectations_1']=raw
   result=self.scorer.score(source,epi_applicable=True)
   self.assertIsNone(result.scores['EPI'].value)
   self.assertEqual(result.scores['EPI'].issues[0].state,'invalid')
 def test_caller_inputs_unchanged_and_permissions_not_inferred(self):
  source=copy.deepcopy(self.base);reasons={'k6_1':'refused'};context={'event':'synthetic','country':'GH'}
  before=copy.deepcopy((source,reasons,context,self.contract))
  r=self.scorer.score(source,missingness=reasons,source_context=context)
  self.assertEqual((source,reasons,context,self.contract),before)
  self.assertTrue(r.provisional)
  self.assertIsNone(r.scores['EPI'].value)
  self.assertIsNone(r.scores['NSES'].value)
  self.assertFalse(any('burden' in k.lower() or 'cohort' in k.lower() for k in r.scores))
