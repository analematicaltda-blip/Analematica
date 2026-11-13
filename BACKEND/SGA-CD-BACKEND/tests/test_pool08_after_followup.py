"""Real SGA CRM transactions; reservation/beneficiary qualification remains separate."""
import runpy,unittest,uuid
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('test_pool08_crm.py')),run_name='followup_sga_fixture')
from app.commercial.pool08.crm_api import service
from app.commercial.pool08.after_sales_followup import record_followup
from app.commercial.pool08.crm import CRMError
from app.models.user import Usuario
from starlette.datastructures import QueryParams
class FollowupChecks(unittest.TestCase):
 def setUp(self):
  fixture['CRMChecks'].setUp(self);self.contact=fixture['CRMChecks'].create(self);self.reservation=str(uuid.uuid4())
 tearDown=fixture['CRMChecks'].tearDown
 login=fixture['CRMChecks'].login
 post=fixture['CRMChecks'].post
 cmd=fixture['CRMChecks'].cmd
 def crm(self,db=None,other=False):
  db=db or self.db;return service(SimpleNamespace(method='POST',query_params=QueryParams()),db,db.get(Usuario,self.users['other-admin_empresa' if other else 'full-admin_empresa']))
 def payload(self):return dict(request_id=str(uuid.uuid4()),contact_id=self.contact,expected_revision=1,reservation_id=self.reservation,title='Internal synthetic followup',due_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat().replace('+00:00','Z'),responsible_ref=str(self.users['full-admin_empresa']))
 def test_replay_retains_raw_request_but_new_uuid_cannot_duplicate(self):
  data=self.payload();record_followup(self.crm(),data);self.assertTrue(record_followup(self.crm(),data)['replayed'])
  with self.assertRaises(CRMError) as caught:record_followup(self.crm(),{**data,'request_id':str(uuid.uuid4()),'expected_revision':2})
  self.assertEqual(str(caught.exception),'FOLLOWUP_ALREADY_RECORDED');self.assertEqual(len(self.crm().get(self.contact)['tasks']),1)
 def test_same_instant_with_another_timezone_encoding_is_duplicate(self):
  data=self.payload();record_followup(self.crm(),data)
  with self.assertRaises(CRMError) as caught:record_followup(self.crm(),{**data,'request_id':str(uuid.uuid4()),'expected_revision':2,'due_at':data['due_at'].replace('Z','+00:00')})
  self.assertEqual(str(caught.exception),'FOLLOWUP_ALREADY_RECORDED')
 def test_reusing_uuid_with_another_command_conflicts(self):
  data=self.payload();record_followup(self.crm(),data)
  with self.assertRaises(CRMError) as caught:record_followup(self.crm(),{**data,'title':'Other command'})
  self.assertEqual(str(caught.exception),'REQUEST_CONFLICT')
 def test_audit_failure_rolls_back_task_and_event(self):
  crm=self.crm();before=crm.history(self.contact)
  with patch.object(type(crm.store),'append',side_effect=RuntimeError('Synthetic audit failure')):
   with self.assertRaises(RuntimeError):record_followup(crm,self.payload())
  self.assertEqual(self.crm().get(self.contact)['tasks'],[]);self.assertEqual(self.crm().history(self.contact),before)
 def test_foreign_company_cannot_attach_a_task(self):
  with self.assertRaises(CRMError) as caught:record_followup(self.crm(other=True),self.payload())
  self.assertEqual(caught.exception.status,404);self.assertEqual(self.crm().get(self.contact)['tasks'],[])
 def test_two_connections_cannot_create_two_equal_followups(self):
  from concurrent.futures import ThreadPoolExecutor
  from threading import Barrier
  barrier=Barrier(2);data=self.payload()
  def writer(index):
   with self.factory() as db:
    crm=self.crm(db);barrier.wait(timeout=10)
    try:record_followup(crm,{**data,'request_id':str(uuid.uuid4())});return 200
    except CRMError as exc:return exc.status
  with ThreadPoolExecutor(max_workers=2) as workers:self.assertEqual(sorted(workers.map(writer,range(2))),[200,409])
  self.assertEqual(len(self.crm().get(self.contact)['tasks']),1)
if __name__=='__main__':unittest.main(verbosity=2)
