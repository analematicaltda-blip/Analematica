"""Real private HTTP traces and bounded concurrent local measurements; no SLA claim."""
import runpy,unittest,uuid,json,time,os,statistics
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='operations_http_fixture');base=f['CRMHTTPChecks']
class Checks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__);tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_owned_audit_trace_permissions_and_no_store(self):
  for system,c,q,p in self.targets():
   suffix='' if system=='sga-cd' else '/';body={'request_id':str(uuid.uuid4()),'operation':'prepare','job_id':None,'expected_revision':0,'data':{'question':'revisar contactos','tools':[],'modality':'TEXT','engine':'none'}};ref=self.unwrap(c.post(p+'crm/army-commands'+suffix,params=q,json=body))['job_id'];r=c.get(p+'crm/operations/army/'+ref+suffix,params=q);d=self.unwrap(r);self.assertTrue(d['chain_verified']);self.assertEqual(len(d['events']),1);self.assertNotIn('receipt',d['events'][0]);self.assertIn('no-store',r.headers.get('cache-control',''));cred=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.get(p+'crm/operations/army/'+ref+suffix,params=q,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,(403,404));self.assertIn(c.get(p+'crm/operations'+suffix,params=q,headers={'Authorization':''}).status_code,(401,403));self.assertIn(c.get(p+'crm/operations/unknown/'+ref+suffix,params=q).status_code,(400,404));self.assertIn(c.post(p+'crm/operations'+suffix,params=q,json={}).status_code,(404,405))
 def test_measured_concurrent_read_only_probe(self):
  measurements=[]
  for system,c,q,p in self.targets():
   suffix='' if system=='sga-cd' else '/'
   def sample(_):
    start=time.perf_counter();r=c.get(p+'crm/operations'+suffix,params=q);d=self.unwrap(r);self.assertEqual(d['provider_calls'],0);self.assertEqual(d['ledger_writes'],0);self.assertFalse(d['hardware_or_production_qualified']);self.assertTrue(all(x['sample_count'] is None for x in d['sources'] if x['state']=='UNAVAILABLE'));return round((time.perf_counter()-start)*1000,3)
   sample(0)
   with ThreadPoolExecutor(max_workers=4) as workers:values=sorted(workers.map(sample,range(8)))
   measurements.append({'system':system,'samples':8,'concurrency':4,'p50_ms':statistics.median(values),'p95_ms':values[-1],'max_ms':max(values),'scope':'LOOPBACK_OPERATIONAL_READ_PROBE','production_sla_qualified':False,'provider_latency_measured':False})
  output=Path(os.environ.get('COMMERCIAL_OPS_BENCHMARK','/tmp/gc024-operations-benchmark.json'));output.write_text(json.dumps({'measurements':measurements,'hardware_target':False,'data':'synthetic disposable scoped records','sla_accepted':False},indent=2)+'\n')
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
