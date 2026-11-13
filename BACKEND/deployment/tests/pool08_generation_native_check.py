"""Native generation jobs with real ORM/API and controlled inference transport."""
import importlib,runpy,unittest,os,json
from pathlib import Path
from unittest.mock import patch
from pool08_generation_cases import GenerationCases
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_library_native_check.py')),run_name='generation_native_setup')
from django.db import connection
for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 m=importlib.import_module(path+'.generation_models')
 with connection.schema_editor() as editor:
  for model in (m.GenerationJob,m.GenerationEvent,m.GenerationResult):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

def cases(system,path):
 module=importlib.import_module(path+'.generation');store=importlib.import_module(path+'.generation_store');models=importlib.import_module(path+'.generation_models')
 class Checks(GenerationCases,unittest.TestCase):
  module_path=path
  def setUp(self):
   self.c=fixture['cases'](system,path)();self.c.setUp();self.addCleanup(self.c.doCleanups);crm=self.c.engine().crm;self.gen=module.Generation(store.Store(crm.store),crm);self.error=module.CRMError;self.providers=importlib.import_module(path+'.generation_providers')
   self.config_key=system+':'+self.gen.store.scope+':'+self.gen.store.provider;profile={'adapter':'ollama','model':'copy:1','model_digest':'a'*64,'rights_note':'Declaración de laboratorio, no cualificada','cost_units':100,'max_output_tokens':64};self.config={self.config_key:{'text':profile,'image':{**profile,'adapter':'sd-webui','model':'diffusion-one'}}};env=patch.dict(os.environ,{'COMMERCIAL_GENERATION_PROFILES':json.dumps(self.config)});env.start();self.addCleanup(env.stop)
  def corrupt_result(self,ref):models.GenerationResult.objects.filter(pk=ref).update(data=b'corrupt')
  def corrupt_event(self,ref):models.GenerationEvent.objects.filter(item_id=ref).update(item_id='corrupt')
  def test_generation_audit_failure_rolls_back_job(self):
   with patch.object(models.GenerationEvent.objects,'create',side_effect=RuntimeError('synthetic audit failure')):
    with self.assertRaises(RuntimeError):self.create()
   self.assertEqual(models.GenerationJob.objects.filter(scope=self.gen.store.scope).count(),0)
  def test_revoked_owner_cannot_claim_or_read_result(self):
   from apps.turismo.models import VerifiedCompanyLink
   from django.utils import timezone
   ref=self.create();link=VerifiedCompanyLink.objects.filter(provider_id=self.gen.store.provider).get();link.revoked_at=timezone.now();link.save()
   with self.assertRaises(Exception):self.gen.claim(ref)
   self.assertIsNone(self.gen.store.result(ref))
 Checks.__name__=system.replace('-','')+'Generation';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
