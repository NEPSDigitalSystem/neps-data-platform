"""Independent scorer safety checks outside implementation-authored suite."""
import copy,json
from pathlib import Path
from fractions import Fraction
import unittest
import hashlib
from unittest.mock import patch
from etl.scoring.v31 import Scorer
from etl.sync.v31_workflow import serialise
ROOT=Path(__file__).resolve().parents[1]
class IndependentScoringQA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.contract=json.loads((ROOT/'etl/contracts/data_contract_v31.json').read_text(encoding="utf-8"))
  cls.scorer=Scorer(cls.contract)
  gold=json.loads((ROOT/'tests/fixtures/SCORING_GOLDEN.json').read_text(encoding="utf-8"))
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

 def test_each_group_endpoints_and_independent_interior_arithmetic(self):
  # Field groups and arithmetic transcribed from manual sections 3A through 3E.
  # No scorer group, code list or normalization helper supplies expectations.
  cases=[]
  for prefix in ['expectations','failure','caregivers','future','progress']:
   cases.append(('EPI',[f'epi_{prefix}_{i}' for i in (1,2)],
                 [([1,1],0),([1,4],Fraction(75,2)),([5,5],100)]))
  for prefix in ['finstrain','food','educost','materials','transport']:
   cases.append(('ESI',[f'esi_{prefix}_{i}' for i in (1,2)],
                 [([0,0],0),([0,3],Fraction(75,2)),([4,4],100)]))
  for prefix,count,raw,interior in [
   ('loved',8,[1,2,3,4,5,4,3,2],50),('comm',4,[1,2,4,5],50),
   ('self',4,[1,2,4,5],50),('help',3,[1,2,4],Fraction(100,3))]:
   cases.append(('SBI',[f'sbi_{prefix}_{i}' for i in range(1,count+1)],
                 [([1]*count,0),(raw,interior),([5]*count,100)]))
  cases.extend([
   ('MHDI',[f'k6_{i}' for i in range(1,7)],
    [([0]*6,0),([0,1,2,3,4,1],Fraction(275,6)),([4]*6,100)]),
   ('BRS_100',[f'brs_{i:02}' for i in range(1,7)],
    [([1,5,1,5,1,5],0),([1,4,3,2,5,4],Fraction(275,6)),([5,1,5,1,5,1],100)]),
   ('MSPSS_100',[f'mspss_{i:02}' for i in range(1,13)],
    [([1]*12,0),([1,2,3,4,5,6,7,6,5,4,3,2],50),([7]*12,100)]),
   ('GSE_100',[f'gse_{i:02}' for i in range(1,11)],
    [([1]*10,0),([1,2,3,4,1,2,3,4,1,2],Fraction(130,3)),([4]*10,100)]),
  ])
  for index,names,examples in cases:
   for raw,normalized in examples:
    with self.subTest(index=index,group=names[0],raw=raw):
     source=dict(self.base,**dict(zip(names,map(str,raw))))
     expected={'EPI':0,'ESI':0,'SBI':0,'MHDI':0,'K6_total':0,
               'BRS_100':100,'MSPSS_100':100,'GSE_100':100,'PFI':100,'NSES':0}
     normalized=Fraction(normalized)
     if index in ('EPI','ESI','SBI'):
      expected[index]=normalized/(4 if index=='SBI' else 5)
      expected['NSES']=expected[index]*{'EPI':Fraction(3,10),'ESI':Fraction(1,4),'SBI':Fraction(1,5)}[index]
     elif index=='MHDI':
      expected['MHDI']=normalized
      expected['K6_total']=sum(raw)
      expected['NSES']=normalized/5
     else:
      expected[index]=normalized
      expected['PFI']=(200+normalized)/3
      expected['NSES']=(100-normalized)/60
     result=self.scorer.score(source,epi_applicable=True)
     self.assertEqual({n:s.value for n,s in result.scores.items()},expected)
     self.assertTrue(all(not s.issues for s in result.scores.values()))

 def test_each_reversed_item_all_native_values(self):
  # Starting with maximum protection, increasing one reversed raw item must
  # reduce BRS and PFI, and increase the protective-deficit NSES contribution.
  for name in ('brs_02','brs_04','brs_06'):
   for raw,expected in zip(range(1,6),[100,Fraction(575,6),Fraction(275,3),Fraction(175,2),Fraction(250,3)]):
    with self.subTest(field=name,raw=raw):
     source=dict(self.base,**{name:str(raw)})
     result=self.scorer.score(source,epi_applicable=True)
     self.assertEqual(source[name],str(raw))
     self.assertEqual(result.scores['BRS_100'].value,expected)
     self.assertEqual(result.scores['PFI'].value,(200+Fraction(expected))/3)
     self.assertEqual(result.scores['NSES'].value,(100-Fraction(expected))/60)

 def test_every_item_rejects_adjacent_and_undeclared_special_codes(self):
  for name in self.contract['core_73_fields']:
   lower,upper=(0,4) if name.startswith(('esi_','k6_')) else (1,7) if name.startswith('mspss_') else (1,4) if name.startswith('gse_') else (1,5)
   for raw in (lower-1,upper+1,96,98,99):
    with self.subTest(field=name,raw=raw):
     source=dict(self.base,**{name:str(raw)})
     result=self.scorer.score(source,epi_applicable=True)
     self.assertIsNone(result.scores['NSES'].value)
     self.assertEqual([(i.field,i.state) for i in result.scores['NSES'].issues],[(name,'invalid')])
     self.assertEqual(source[name],str(raw))

 def test_semantic_states_propagate_before_reversing_or_aggregating(self):
  for name in ('epi_expectations_1','esi_food_1','sbi_help_1','k6_1','brs_02','mspss_01','gse_01'):
   for state in ('missing','refused','unknown','not_applicable','invalid'):
    with self.subTest(field=name,state=state):
     # An explicit unavailable reason takes precedence even over a numeric raw
     # answer. It never rewrites that answer or creates a numeric contribution.
     source=copy.deepcopy(self.base);reasons={name:state}
     result=self.scorer.score(source,epi_applicable=True,missingness=reasons)
     self.assertIsNone(result.scores['NSES'].value)
     self.assertEqual([(i.field,i.state) for i in result.scores['NSES'].issues],[(name,state)])
     self.assertEqual(source,self.base)
     self.assertEqual(reasons,{name:state})

 def test_integer_codes_match_native_strings_without_coercing_inputs(self):
  integers={name:int(raw) for name,raw in self.base.items()}
  before=copy.deepcopy(integers)
  a=self.scorer.score(integers,epi_applicable=True)
  b=self.scorer.score(self.base,epi_applicable=True)
  self.assertEqual(a.scores,b.scores)
  self.assertNotEqual(a.source_sha256,b.source_sha256)
  self.assertEqual(integers,before)

 def test_exact_fraction_json_boundary_and_unavailable_values(self):
  gold=json.loads((ROOT/'tests/fixtures/SCORING_GOLDEN.json').read_text(encoding='utf-8'))
  source=next(c['responses'] for c in gold['cases'] if c['id']=='all_midpoint')
  result=self.scorer.score(source,epi_applicable=True)
  self.assertEqual(result.scores['K6_total'].value,Fraction(12))
  self.assertEqual(result.scores['PFI'].value,Fraction(100,3))
  self.assertEqual(result.scores['NSES'].value,Fraction(305,6))
  stored=json.loads(json.dumps(serialise(result),allow_nan=False))
  self.assertEqual(stored['scores']['PFI']['value'],{'numerator':100,'denominator':3})
  self.assertEqual(stored['scores']['NSES']['value'],{'numerator':305,'denominator':6})
  for name,score in result.scores.items():
   value=stored['scores'][name]['value']
   self.assertEqual(Fraction(value['numerator'],value['denominator']),score.value)
  self.assertEqual(stored['algorithm_version'],result.algorithm_version)
  self.assertEqual(stored['source_sha256'],result.source_sha256)
  self.assertEqual(stored['contract_sha256'],result.contract_sha256)
  self.assertTrue(stored['provisional'])
  unavailable=serialise(self.scorer.score(source))
  self.assertIsNone(unavailable['scores']['EPI']['value'])
  self.assertEqual(unavailable['scores']['EPI']['issues'],[{'field':'EPI','state':'applicability_unverified'}])

 def test_provenance_hashes_inputs_contract_and_scoring_code(self):
  def digest(value):
   data=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')
   return hashlib.sha256(data).hexdigest()
  context={'project':'synthetic','event':'baseline','instance':'1'}
  result=self.scorer.score(self.base,epi_applicable=True,source_context=context)
  contract_hash=digest(self.contract)
  source_hash=digest({'responses':self.base,'missingness':{},'epi_applicable':True,'source_context':context})
  code_hash=hashlib.sha256((ROOT/'etl/scoring/v31.py').read_bytes()).hexdigest()
  self.assertEqual(result.contract_sha256,contract_hash)
  self.assertEqual(result.source_sha256,source_hash)
  suffix=digest({'contract':contract_hash,'code':code_hash})
  self.assertEqual(result.algorithm_version,'NEPS-V3.1-provisional-corrected-1;complete-items-only;equal-dimensions:'+suffix)
  reordered=dict(reversed(list(self.base.items())))
  self.assertEqual(result,self.scorer.score(reordered,epi_applicable=True,source_context=dict(reversed(list(context.items())))))
  extra=dict(self.base,epi_exam_1='5',nses_100='99',unrecognized_extra='synthetic')
  self.assertEqual(result,self.scorer.score(extra,epi_applicable=True,source_context=context))
  self.assertNotEqual(result.source_sha256,self.scorer.score(self.base,source_context=context).source_sha256)
  with patch('etl.scoring.v31.Path.read_bytes',return_value=b'synthetic scoring code revision'):
   revised=Scorer(self.contract).score(self.base,epi_applicable=True,source_context=context)
  self.assertNotEqual(result.algorithm_version,revised.algorithm_version)
  self.assertEqual(result.contract_sha256,revised.contract_sha256)
  self.assertEqual(result.source_sha256,revised.source_sha256)
  self.assertEqual(result.scores,revised.scores)

 def test_non_core_semantic_field_is_rejected(self):
  with self.assertRaises(ValueError):
   self.scorer.score(self.base,missingness={'epi_exam_1':'not_applicable'})
