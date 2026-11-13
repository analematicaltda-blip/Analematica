"""Owned reports over real HTTP and the authenticated Analematica gateway."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='analytics_http_setup');base=f['CRMHTTPChecks']
class Checks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__);tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_report_routes_idempotency_and_isolation(self):
  day=datetime.now(ZoneInfo('America/Bogota')).date()
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    suffix='' if system=='sga-cd' else '/';body={'request_id':str(uuid.uuid4()),'operation':'build','job_id':None,'expected_revision':0,'data':{'since':(day-timedelta(days=30)).isoformat(),'until':day.isoformat(),'provider_reads':False,'confirmed_scope':True}};url=p+'crm/analytics-commands'+suffix;receipt=self.unwrap(c.post(url,params=q,json=body));ref=receipt['job_id'];self.assertTrue(self.unwrap(c.post(url,params=q,json=body))['replayed']);report=self.unwrap(c.get(p+'crm/analytics/'+ref+suffix,params=q));self.assertIn(report['status'],('PARTIAL','SOURCE_SNAPSHOT'));self.assertEqual(report['revision'],2);self.assertFalse(report['report']['fiscal_or_bank_action_executed']);self.assertEqual(len(self.unwrap(c.get(p+'crm/analytics/'+ref+'/history'+suffix,params=q))['events']),2);self.assertEqual(self.unwrap(c.get(p+'crm/analytics-receipts/'+body['request_id']+suffix,params=q))['job_id'],ref)
    credentials=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.get(p+'crm/analytics/'+ref+suffix,params=q,headers={'Authorization':'Bearer '+credentials['other_token']}).status_code,(403,404));self.assertIn(c.get(p+'crm/analytics'+suffix,params=q,headers={'Authorization':''}).status_code,(401,403))
 def test_request_limits_and_no_arbitrary_query(self):
  for system,c,q,p in self.targets():
   suffix='' if system=='sga-cd' else '/';url=p+'crm/analytics-commands'+suffix;self.assertEqual(c.post(url,params=q,content=' '*17000,headers={'Content-Type':'application/json'}).status_code,413);body={'request_id':str(uuid.uuid4()),'operation':'build','job_id':None,'expected_revision':0,'data':{'sql':'SELECT *'}};self.assertIn(c.post(url,params=q,json=body).status_code,(400,422))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
