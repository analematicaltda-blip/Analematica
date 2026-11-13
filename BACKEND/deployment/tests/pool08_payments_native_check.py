"""Owned durable payment intentions in both native systems; provider success is synthetic.
No authentic Bold confirmation or payment settlement is accredited by this suite.
"""
import runpy,unittest,importlib,uuid,os
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_sales_native_check.py')),run_name='payment_native_fixture')
from django.db import connection
from rest_framework.test import APIRequestFactory,force_authenticate
from pool08_pricing_cases import PricingCases
from apps.core_erp.accounting.models import JournalEntry
for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 models=importlib.import_module(path+'.payment_models')
 with connection.schema_editor() as editor:
  for model in (models.CommercialPayment,models.PaymentEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)
def cases(system,path):
 api=importlib.import_module(path+'.crm_api');module=importlib.import_module(path+'.payments');models=importlib.import_module(path+'.payment_models');gateway=importlib.import_module(path+'.bold_gateway');base=fixture['ERP' if system=='erp-tur' else 'Ana']
 class Checks(unittest.TestCase):
  def setUp(self):
   self.c=base();self.c.setUp();self.addCleanup(self.c.doCleanups);self.calls=[]
   self.fake=gateway.BoldGateway('synthetic-only-identity','synthetic-only-secret',self.send);p=patch.object(module,'runtime_gateway',return_value=self.fake);p.start();self.addCleanup(p.stop)
  def tearDown(self):self.c.tearDown()
  def send(self,body):
   self.calls.append(body);self.assertEqual(models.CommercialPayment.objects.get(scope=str(self.c.base.tenant.pk)).status,'DISPATCHING');return {'payload':{'id':'bold-link-fixture','url':'https://checkout.bold.co/payment/fixture','reference':body['reference']}}
  def body(self,op='create',ref=None,rev=0,**data):return dict(request_id=str(uuid.uuid4()),operation=op,payment_id=ref,expected_revision=rev,data=data)
  def call(self,body=None,ref=None,section='list',user=None):
   r=APIRequestFactory().post('/fixture/?provider_id='+str(self.c.base.provider.pk),body,format='json') if body else APIRequestFactory().get('/fixture/?provider_id='+str(self.c.base.provider.pk));force_authenticate(r,user=user or self.c.base.user);return api.PaymentsView.as_view()(r,section='commands' if body else section,**({'payment_id':ref} if ref else {}))
  def sale(self,confirmed=True):
   price=self.c.q.price_call(PricingCases.body(self,**PricingCases.values(self,unit_price='100.00'))).data['item_id'];quote=self.c.q.create(price);ref=self.c.create(quote)
   if confirmed:self.c.confirm(ref)
   return ref
  def create(self):
   sale=self.sale();r=self.call(self.body(sale_id=sale,confirmed=True));self.assertEqual(r.status_code,200,r.data);return r.data['payment_id']
  def test_source_amount_and_unique_reference_are_server_owned(self):
   ref=self.create();r=self.call(ref=ref).data;self.assertEqual(r['amount'],'119.00');self.assertEqual(len(r['reference']),36);self.assertNotIn('@',r['reference']);self.assertFalse(r['payment_verified'])
  def test_checkout_persists_before_send_and_replay_never_sends_twice(self):
   ref=self.create();body=self.body('checkout',ref,1,confirmed=True);a=self.call(body);self.assertEqual(a.status_code,200,a.data);self.assertEqual(a.data['status'],'CHECKOUT_READY');b=self.call(body);self.assertTrue(b.data['replayed']);self.assertEqual(len(self.calls),1);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.c.base.tenant).count(),1);self.assertFalse(a.data['ledger_written']);self.assertFalse(a.data['payment_verified'])
  def test_unknown_result_blocks_new_nonce_and_read_only_recovery(self):
   ref=self.create()
   def timeout(body):self.calls.append(body);raise TimeoutError()
   self.fake.sender=timeout;r=self.call(self.body('checkout',ref,1,confirmed=True));self.assertEqual(r.data['status'],'UNKNOWN');self.assertEqual(self.call(self.body('checkout',ref,3,confirmed=True)).status_code,409);r=self.call(self.body('recover',ref,3));self.assertEqual(r.status_code,200,r.data);self.assertEqual(len(self.calls),1);self.assertFalse(r.data['payment_verified'])
  def test_declared_amount_signature_and_paid_fields_cannot_override(self):
   sale=self.sale()
   for extra in [{'amount':'1.00'},{'payment_verified':True},{'signature':'fake'}]:self.assertEqual(self.call(self.body(sale_id=sale,confirmed=True,**extra)).status_code,422)
  def test_draft_sale_and_other_owner_are_rejected(self):
   sale=self.sale(False);self.assertEqual(self.call(self.body(sale_id=sale,confirmed=True)).status_code,409);self.assertEqual(self.call(user=self.c.base.other).status_code,403)
  def test_one_intent_per_sale_and_no_local_paid_command(self):
   ref=self.create();sale=self.call(ref=ref).data['sale_id'];self.assertEqual(self.call(self.body(sale_id=sale,confirmed=True)).status_code,409);self.assertEqual(self.call(self.body('confirm',ref,1,paid=True)).status_code,422);self.assertEqual(len(self.calls),0)
  def test_outstanding_checkout_blocks_sale_reversal(self):
   ref=self.create();self.call(self.body('checkout',ref,1,confirmed=True));sale=self.call(ref=ref).data['sale_id'];r=self.c.call(self.c.body('review_reversal',sale,3,reason='Debe conciliarse el enlace antes de revertir',support_digest='e'*64,confirmed=True));self.assertEqual(r.status_code,409,r.data)
  def test_index_metadata_tamper_does_not_free_sale_or_duplicate_intent(self):
   ref=self.create();self.call(self.body('checkout',ref,1,confirmed=True));row=models.CommercialPayment.objects.get(pk=ref);sale=row.document['sale_id'];models.CommercialPayment.objects.filter(pk=ref).update(code='ALTERED',status='CANCELLED');self.assertEqual(self.call(ref=ref).status_code,503);self.assertEqual(self.call(self.body(sale_id=sale,confirmed=True)).status_code,503);r=self.c.call(self.c.body('review_reversal',sale,3,reason='Debe conciliarse',support_digest='e'*64,confirmed=True));self.assertEqual(r.status_code,503,r.data)
  def test_unqualified_provider_amount_is_a_domain_rejection_not_server_error(self):
   price=self.c.q.price_call(PricingCases.body(self,**PricingCases.values(self,unit_price='1000000000000.00'))).data['item_id'];quote=self.c.q.create(price);sale=self.c.create(quote);self.c.confirm(sale);r=self.call(self.body(sale_id=sale,confirmed=True));self.assertEqual(r.status_code,409,r.data);self.assertEqual(r.data['code'],'PAYMENT_AMOUNT_NOT_QUALIFIED');self.assertEqual(self.calls,[])
  def test_audit_failure_rolls_back_creation(self):
   sale=self.sale()
   with patch.object(models.PaymentEvent.objects,'create',side_effect=RuntimeError('synthetic audit failure')):
    with self.assertRaises(RuntimeError):self.call(self.body(sale_id=sale,confirmed=True))
   self.assertEqual(models.CommercialPayment.objects.filter(scope=str(self.c.base.tenant.pk)).count(),0)
 Checks.__name__=system.replace('-','_')+'PaymentIntents';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
