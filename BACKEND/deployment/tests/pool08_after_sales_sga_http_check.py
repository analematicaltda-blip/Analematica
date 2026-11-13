"""Actual SGA HTTP -> reviewed native JWT/HMAC source -> cancellation policy engine.
Loopback transport and disposable native connection; no bank or physical acceptance.
"""
import runpy,unittest,uuid,importlib
from pathlib import Path
from django.db import connection
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_sales_saga_http_check.py')),run_name='after_sales_source_http_fixture')
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.models import PoliticaCancelacion
from apps.domain_business.operativa.models import Reservation
created=set();visiting=set()
def create(model):
 model=model._meta.concrete_model
 if model in visiting or model._meta.db_table in connection.introspection.table_names():return
 visiting.add(model)
 for f in model._meta.local_fields:
  if f.is_relation and f.remote_field and f.remote_field.model is not model:create(f.remote_field.model)
 for f in model._meta.local_many_to_many:create(f.remote_field.model)
 with connection.schema_editor() as editor:editor.create_model(model)
 visiting.remove(model)
for model in (PoliticaCancelacion,Reservation):create(model)
class Checks(fixture['HTTPChecks']):
 def setUp(self):
  super().setUp()
  from app.commercial.pool08.api import router
  self.s.client.app.include_router(router,prefix='/api/v1/commercial-unified')
  from rest_framework_simplejwt.tokens import AccessToken
  self.headers={'X-Native-Ledger-Authorization':'Bearer '+str(AccessToken.for_user(self.n.base.user))}
 def after(self,op,data,provider=None):return self.s.client.post('/api/v1/commercial-unified/crm/after-sales/'+op,json={'provider_id':provider or str(self.n.base.provider.pk),'data':data},headers=self.headers)
 def test_scoped_policy_review_publish_and_replay_from_sga(self):
  from django.utils import timezone
  day=timezone.localdate().isoformat();config=dict(name='Política posventa SGA',terms='Condiciones de prueba con excepciones explícitas',scope='SERVICIO',percentage='40.00',basis='REQUESTED_REFUND',active=True,valid_from=day,valid_until=day,timing_tiers=[dict(min_days_before=30,percentage='5.00'),dict(min_days_before=15,percentage='10.00'),dict(min_days_before=7,percentage='20.00'),dict(min_days_before=0,percentage='40.00')])
  r=self.after('review_policy',dict(request_id=str(uuid.uuid4()),policy_id=None,expected_revision=0,values=config,confirmed=True));self.assertEqual(r.status_code,200,r.text);review=r.json()['result'];body=dict(review_id=review['review_id'],confirmed=True);r=self.after('publish_policy',body);self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['result']['money_transferred']);self.assertTrue(self.after('publish_policy',body).json()['result']['replayed']);self.assertEqual(len(self.after('sources',{'policy_after':None,'reservation_after':None}).json()['result']['policies']),1)
 def test_foreign_mapping_and_forged_actor_fail_closed(self):
  r=self.after('sources',{'policy_after':None,'reservation_after':None},str(uuid.uuid4()));self.assertIn(r.status_code,(403,503));r=self.after('sources',{'policy_after':None,'reservation_after':None,'actor':'forged'});self.assertIn(r.status_code,(422,503))
if __name__=='__main__':unittest.main()
