"""Independent source-scope QA using synthetic transport only."""
import unittest
from test_v31_connector import Session, Response, native_metadata, settings
from etl.extract.production_client import ProductionRedcapClient, RedcapClientError
class IndependentConnectorQA(unittest.TestCase):
 def client(self,rows):
  return ProductionRedcapClient(settings(),session=Session(Response(native_metadata()),Response(rows)),authorisation_provider=lambda _:True,sleep=lambda _:None)
 def test_record_subset_response_mismatch_rejected(self):
  for row in [{'study_id':'OTHER','redcap_event_name':'baseline'},{'redcap_event_name':'baseline'},{'study_id':None,'redcap_event_name':'baseline'}]:
   with self.subTest(row=row),self.assertRaises(RedcapClientError):
    self.client([row]).export_records(records=['SYN-1'],events=['baseline'])
 def test_event_subset_response_mismatch_rejected(self):
  for event in ['month6',None]:
   row={'study_id':'SYN-1','redcap_event_name':event}
   with self.subTest(event=event),self.assertRaises(RedcapClientError):
    self.client([row]).export_records(records=['SYN-1'],events=['baseline'])
 def test_record_subset_valid_is_not_relabelled(self):
  row={'study_id':'SYN-1','redcap_event_name':'baseline','redcap_repeat_instrument':'neps31_yeb','redcap_repeat_instance':'2','k6_1':''}
  self.assertEqual(self.client([row]).export_records(records=['SYN-1'],events=['baseline']),[row])
