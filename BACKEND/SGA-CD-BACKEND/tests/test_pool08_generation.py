"""Own SQLAlchemy generation queue, audit, rights and local-model protocol boundary."""
import runpy,unittest,os,json,sys,importlib
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'deployment/tests'))
from pool08_generation_cases import GenerationCases
fixture=runpy.run_path(str(Path(__file__).with_name('test_pool08_library.py')),run_name='generation_sga_setup')
from app.commercial.pool08 import generation as domain,generation_store as store,generation_models as models,generation_providers
from app.commercial.pool08.crm_api import service
from app.models.user import Usuario
from starlette.datastructures import QueryParams
class Checks(GenerationCases,unittest.TestCase):
 module_path='app.commercial.pool08'
 def setUp(self):
  self.c=fixture['Checks']();self.c.setUp();self.addCleanup(self.c.tearDown);crm=service(SimpleNamespace(method='POST',query_params=QueryParams()),self.c.db,self.c.db.get(Usuario,self.c.users['full-admin_empresa']));self.gen=domain.Generation(store.Store(crm.store),crm);self.error=domain.CRMError;self.providers=generation_providers
  self.config_key='sga-cd:'+self.gen.store.scope+':-';p={'adapter':'ollama','model':'copy:1','model_digest':'a'*64,'rights_note':'Declaración de laboratorio, no cualificada','cost_units':100,'max_output_tokens':64};self.config={self.config_key:{'text':p,'image':{**p,'adapter':'sd-webui','model':'diffusion-one'}}};env=patch.dict(os.environ,{'COMMERCIAL_GENERATION_PROFILES':json.dumps(self.config)});env.start();self.addCleanup(env.stop)
 def corrupt_result(self,ref):self.c.db.query(models.GenerationResult).filter_by(id=ref).update({'data':b'corrupt'});self.c.db.commit()
 def corrupt_event(self,ref):self.c.db.query(models.GenerationEvent).filter_by(item_id=ref).update({'item_id':'corrupt'});self.c.db.commit()
 def test_generation_event_failure_rolls_back_job(self):
  from sqlalchemy import event
  def fail(*args):raise RuntimeError('synthetic audit failure')
  event.listen(models.GenerationEvent,'before_insert',fail)
  try:
   with self.assertRaises(RuntimeError):self.create()
  finally:event.remove(models.GenerationEvent,'before_insert',fail)
  self.assertEqual(self.c.db.query(models.GenerationJob).count(),0)
if __name__=='__main__':unittest.main()
