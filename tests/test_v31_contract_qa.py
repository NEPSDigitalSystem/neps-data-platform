"""Independent adversarial QA for local source-contract acceptance."""
import copy
import csv
import json
from pathlib import Path
import unittest
from etl.contracts.v31 import build_contract, ContractError
ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = ROOT / 'tests/fixtures/v31_reference'
HEADERS = ['Variable / Field Name', 'Form Name', 'Section Header', 'Field Type', 'Field Label', 'Choices, Calculations, OR Slider Labels', 'Field Note', 'Text Validation Type OR Show Slider Number', 'Text Validation Min', 'Text Validation Max', 'Identifier?', 'Branching Logic (Show field only if...)', 'Required Field?', 'Custom Alignment', 'Question Number (surveys only)', 'Matrix Group Name', 'Matrix Ranking?', 'Field Annotation']
class IndependentContractQA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.contract=json.loads((ROOT/'etl/contracts/data_contract_v31.json').read_text(encoding="utf-8"))
  cls.dictionary=[x['dictionary_metadata'] for x in cls.contract['fields']]
  cls.mapping=[x['analysis_mapping'] for x in cls.contract['fields'] if x['analysis_mapping']]
  cls.core=[x['analysis_mapping'] for x in cls.contract['fields'] if x['core_73']]
  cls.countries={}
  for s in cls.contract['sources']:
   if 'Country_Display.csv' in s['path'] or 'Display_Manifest.csv' in s['path']:
    p=REFERENCE_ROOT / s['path']
    with p.open(encoding='utf-8-sig') as stream:cls.countries[p.name]=list(csv.DictReader(stream))
 def build(self,dictionary=None,countries=None):
  return build_contract(dictionary if dictionary is not None else self.dictionary,self.mapping,self.mapping,self.core,countries if countries is not None else self.countries,[])
 def test_actual_exact_headers_and_raw_dictionary_equal(self):
  self.assertTrue(all(list(r)==HEADERS for r in self.dictionary))
  p=REFERENCE_ROOT / self.contract['sources'][0]['path']
  with p.open(encoding='utf-8-sig') as stream:source=list(csv.DictReader(stream))
  self.assertEqual(source,self.dictionary)
 def test_every_field_is_explicitly_classified(self):
  self.assertEqual(len(self.contract['fields']),223)
  self.assertTrue(all(x['kind'] for x in self.contract['fields']))
  self.assertEqual(sum(x['respondent_question'] for x in self.contract['fields']),188)
  self.assertEqual(sum(x['core_73'] for x in self.contract['fields']),73)
 def test_renamed_eighteenth_header_must_be_rejected(self):
  changed=copy.deepcopy(self.dictionary)
  for row in changed:row['Undocumented Column']=row.pop('Field Annotation')
  with self.assertRaises(ContractError):self.build(dictionary=changed)
 def test_country_crosswalk_undeclared_stored_code_must_be_rejected(self):
  changed=copy.deepcopy(self.countries)
  changed['Education_Level_Crosswalk_Country_Display.csv'][0]['NEPS_common_code']='999'
  with self.assertRaises(ContractError):self.build(countries=changed)
 def test_country_crosswalk_unrecognised_country_must_be_rejected(self):
  changed=copy.deepcopy(self.countries)
  changed['Education_Level_Crosswalk_Country_Display.csv'][0]['country']='UNVERIFIED COUNTRY'
  with self.assertRaises(ContractError):self.build(countries=changed)
