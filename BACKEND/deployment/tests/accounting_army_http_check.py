"""Real HTTP, native JWT and separate backend-owned armies; no SGA-CD process."""
import json,os,subprocess,sys,tempfile,queue,threading,unittest,uuid
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[3]
class NativeArmiesHTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.servers={};cls.diagnostics={}
  for system in ('erp-tur','analematica','turismo'):
   private=tempfile.TemporaryDirectory(prefix='native-army-http-');cls.addClassCleanup(private.cleanup)
   stderr=tempfile.TemporaryFile();cls.addClassCleanup(stderr.close);cls.diagnostics[system]=stderr
   process=subprocess.Popen([sys.executable,str(Path(__file__).with_name('army_http_fixture.py')),'--system',system,'--directory',private.name],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.PIPE,stderr=stderr,text=True)
   def stop(process=process):
    process.terminate()
    try:process.wait(timeout=8)
    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
    process.stdout.close()
   cls.addClassCleanup(stop)
   ready=queue.Queue()
   def reader(process=process,ready=ready):
    for line in process.stdout:
     if line.startswith('READY '):ready.put(int(line.split()[1]));return
   threading.Thread(target=reader,daemon=True).start()
   try:port=ready.get(timeout=35)
   except queue.Empty:raise RuntimeError('Native backend fixture did not start; private diagnostics retained') from None
   credentials=json.loads((Path(private.name)/'native.json').read_text())
   client=httpx.Client(base_url='http://127.0.0.1:'+str(port),trust_env=False,timeout=15,headers={'Authorization':'Bearer '+credentials['token'],'Host':'localhost'});cls.addClassCleanup(client.close)
   cls.servers[system]=(client,credentials)
 @classmethod
 def tearDownClass(cls):
  for system,stream in cls.diagnostics.items():
   stream.seek(0);path=Path('/tmp/army-http-last-'+system+'.log');path.write_bytes(stream.read()[-24000:]);path.chmod(0o600)
 def unwrap(self,r):
  self.assertEqual(r.status_code,200,r.text);data=r.json();return data['data'] if data.get('success') is True else data
 def mission(self,cred,request=None):return {'request_id':request or str(uuid.uuid4()),'tasks':['trial_balance','profitability'],'since':cred['day'],'until':cred['day'],'confirmed':True}
 def test_native_catalogs_run_without_sga_cd_backend_or_modules(self):
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system];self.assertFalse(cred['sgacd_modules_loaded'])
   data=self.unwrap(client.get('/api/v1/accounting-army/',params={'provider_id':cred['provider_id']}));self.assertEqual(data['system'],system);self.assertEqual(data['logical_agents'],29);self.assertEqual(data['staff']['operational_general'],'JARVI');self.assertEqual(data['staff']['agent_optimizer'],'SOUP')
 def test_jarvi_mission_replay_and_soup_over_actual_http(self):
  request=str(uuid.uuid4())
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system];query={'provider_id':cred['provider_id']};body=self.mission(cred,request)
   first=self.unwrap(client.post('/api/v1/accounting-army/missions/',params=query,json=body));self.assertFalse(first['ledger_written']);self.assertEqual(first['status'],'COMPLETED_READ')
   again=self.unwrap(client.post('/api/v1/accounting-army/missions/',params=query,json=body));self.assertTrue(again['replayed']);self.assertEqual(first['results'],again['results'])
   evaluation=self.unwrap(client.get('/api/v1/accounting-army/missions/'+request+'/optimization/',params=query));self.assertEqual(evaluation['optimizer'],'SOUP');self.assertFalse(evaluation['candidate_activated']);self.assertEqual(evaluation['total_tool_duration_ns'],sum(row['duration_ns'] for row in first['results']))
 def test_neko_text_or_voice_preview_does_not_execute(self):
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system];query={'provider_id':cred['provider_id']}
   request=str(uuid.uuid4());body={'request_id':request,'question':'rentabilidad','since':cred['day'],'until':cred['day'],'modality':'VOICE_TRANSCRIPT'}
   preview=self.unwrap(client.post('/api/v1/accounting-army/intake/',params=query,json=body));self.assertFalse(preview['mission_executed']);self.assertFalse(preview['draft']['confirmed'])
   state=client.get('/api/v1/accounting-army/missions/'+request+'/',params=query);self.assertEqual(state.status_code,400)
 def test_unauthorized_owner_and_unconfigured_engines_do_not_act(self):
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system];query={'provider_id':cred['provider_id']}
   self.assertEqual(client.get('/api/v1/accounting-army/',params=query,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,403)
   mission=self.unwrap(client.post('/api/v1/accounting-army/missions/',params=query,json=self.mission(cred)))
   engine=client.post('/api/v1/accounting-army/missions/'+mission['request_id']+'/engines/open-duet/',params=query,json={'confirmed':True,'share_plan':True});self.assertEqual(engine.status_code,503)
 def test_national_tourism_remains_institutional_without_erp_army_routes(self):
  client,cred=self.servers['turismo']
  for path in ['/api/v1/accounting-army/','/api/v1/governance/plataforma/accounting-army/','/api/admin/plataforma/accounting-army/']:
   self.assertEqual(client.get(path,params={'provider_id':cred['provider_id']}).status_code,404)
if __name__=='__main__':unittest.main(verbosity=2)
