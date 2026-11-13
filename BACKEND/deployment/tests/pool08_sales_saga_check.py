"""Two actual databases, SGA-owned cupos and native canonical ledger.
In-process reviewed RPC adapter injects a lost acknowledgment after the commit;
network/TLS qualification is separate from these transaction/recovery checks.
"""
import runpy,unittest,uuid,copy,importlib,os
from pathlib import Path
from datetime import datetime,timezone,timedelta
from types import SimpleNamespace
from unittest.mock import patch
from starlette.datastructures import QueryParams
root=Path(__file__).resolve().parents[3]
native=runpy.run_path(str(Path(__file__).with_name('pool08_sales_native_check.py')),run_name='saga_native_fixture')
sga=runpy.run_path(str(root/'BACKEND/tests/workspace/test_workspace.py'),run_name='saga_sga_fixture')
from app.commercial.pool08 import crm_api
from app.commercial.pool08.sales_saga import SalesSaga
from app.commercial.pool08.sales_store import Store
from app.commercial.pool08.sales_operations import Operations
from app.commercial.pool08.crm import CRMError
from app.commercial.pool08.install_crm import install
from app.models.user import Usuario
from app.models.academic import Escenario,EscenarioParte,Reserva
from app.commercial.pool08.sales_models import SaleSpaceClaim
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pool08_pricing_cases import PricingCases
from pool08_quotation_cases import QuotationCases
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.core_erp.accounting.models import JournalEntry

class SagaChecks(unittest.TestCase):
 def setUp(self):
  self.n=native['ERP']();self.n.setUp();self.addCleanup(self.n.doCleanups)
  self.s=sga['WorkspaceTests']();self.s.setUp();self.addCleanup(self.s.tearDown);install(self.s.engine,apply=True)
  self.env=patch.dict(os.environ,COMMERCIAL_SALES_SOURCE_KEY='synthetic-saga-source-key-more-than-32',COMMERCIAL_QUOTE_LINK_KEY='synthetic-saga-link-key-more-than-32');self.env.start();self.addCleanup(self.env.stop)
  self.api=importlib.import_module('apps.prestadores.mi_negocio.gestion_comercial.pool08.source_api');self.protocol=importlib.import_module('apps.prestadores.mi_negocio.gestion_comercial.pool08.source_protocol');self.bindings=importlib.import_module('apps.prestadores.mi_negocio.gestion_comercial.pool08.source_binding')
  self.user=self.s.db.get(Usuario,self.s.users['full-admin_empresa']);self.crm=crm_api.service(SimpleNamespace(method='POST',query_params=QueryParams()),self.s.db,self.user);self.quotes=crm_api.make_quotations(self.crm)
  self.context={'system':'sga-cd','scope':self.crm.store.scope,'actor':self.crm.actor,'role_fingerprint':self.crm.authorize().session()['local_role_fingerprint'],'issued_at':datetime.now(timezone.utc).isoformat()}
  self.bindings.review_binding(operator=self.n.base.link.reviewed_by,provider_id=self.n.base.provider.pk,proof=self.protocol.wrap(self.context,{}),valid_until=datetime.now(timezone.utc)+timedelta(hours=1),support_digest='b'*64,apply=True)
  self.peer=SimpleNamespace(rpc=self.rpc);self.drop=False;self.sales=SalesSaga(Store(self.crm.store),self.quotes,Operations(self.quotes),self.peer)
 def tearDown(self):self.n.tearDown()
 def rpc(self,action,body,provider):
  req=APIRequestFactory().post('/source/?provider_id='+provider,self.protocol.wrap({**self.context,'issued_at':datetime.now(timezone.utc).isoformat()},copy.deepcopy(body)),format='json');force_authenticate(req,user=self.n.base.user);r=self.api.SaleSourceView.as_view()(req,action=action)
  if r.status_code!=200:raise CRMError(r.data['code'],r.status_code)
  ctx,result=self.protocol.verify(r.data)
  if self.drop and action=='command' and body['command']['operation'] in ('confirm','reverse','cancel'):
   self.drop=False;raise CRMError('SALE_LEDGER_RESULT_UNCERTAIN',503)
  return result
 def body(self,op='create',ref=None,rev=0,**data):return dict(request_id=str(uuid.uuid4()),operation=op,sale_id=ref,expected_revision=rev,data=data)
 def quote(self):
  cid=self.crm.command(dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data=dict(name='Cliente real del fixture SGA',origin='TEST',responsible_ref=self.crm.actor)))['contact_id'];self.contact=cid
  price=self.quotes.pricing.command(PricingCases.body(self,**PricingCases.values(self)))['item_id']
  scenario=Escenario(inquilino_id=self.user.inquilino_id,nombre='Sala de prueba',capacidad=1);self.s.db.add(scenario);self.s.db.flush();part=EscenarioParte(inquilino_id=self.user.inquilino_id,escenario_id=scenario.id,nombre_parte='Sala',capacidad=1);self.s.db.add(part);self.s.db.commit();self.part=part.id
  self.quotes.command(QuotationCases.body(self,'review_capacity',item_id=price,price_revision=1,mode='REQUIRED',resource_ref=str(part.id),reason='Sala exclusiva revisada',support_digest='a'*64))
  start=datetime.now(timezone.utc)+timedelta(days=2);data=QuotationCases.values(self,price,service_windows=[dict(item_id=price,start_at=start.isoformat(),end_at=(start+timedelta(hours=1)).isoformat())]);qid=self.quotes.command(QuotationCases.body(self,**data))['quotation_id'];self.quotes.command(QuotationCases.body(self,'issue',qid,1));link=self.quotes.command(QuotationCases.body(self,'link',qid,2,confirm_share=True));q=self.quotes.get(qid);self.quotes.accept_link(qid,link['link_id'],link['link_token'],dict(request_id=str(uuid.uuid4()),version=q['version'],content_digest=q['content_digest'],confirmed=True));return qid
 def reviewed(self):
  qid=self.quote();ref=self.sales.command(self.body(quotation_id=qid,provider_id=str(self.n.base.provider.pk)))['sale_id'];self.sales.command(self.body('review',ref,1,**self.n.terms('UNCONDITIONAL_RECEIVABLE')));return ref
 def test_post_with_own_cupo_and_exactly_one_native_journal(self):
  ref=self.reviewed();r=self.sales.command(self.body('confirm',ref,2,confirmed=True));self.assertEqual(r['status'],'CONFIRMED');self.assertTrue(r['ledger_written']);self.assertFalse(r['cross_database_atomic']);self.assertEqual(self.s.db.query(Reserva).count(),1);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.n.base.tenant).count(),1);self.assertFalse(self.quotes.capacity.inspect(str(self.part),datetime.now(timezone.utc)+timedelta(days=2),datetime.now(timezone.utc)+timedelta(days=2,hours=2),1)['available'])
 def test_lost_ack_keeps_claim_then_recovers_without_second_journal(self):
  ref=self.reviewed();self.drop=True;body=self.body('confirm',ref,2,confirmed=True);r=self.sales.command(body);self.assertTrue(r['recovery_required']);self.assertEqual(r['status'],'LEDGER_PENDING');self.assertFalse(r['ledger_written']);self.assertEqual(self.s.db.query(SaleSpaceClaim).filter_by(released=False).count(),1);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.n.base.tenant).count(),1)
  self.assertTrue(self.sales.command(body)['replayed']);r=self.sales.command(self.body('recover',ref,r['revision']));self.assertEqual(r['status'],'CONFIRMED');self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.n.base.tenant).count(),1);self.assertEqual(self.s.db.query(Reserva).count(),1)
 def test_claim_geometry_delete_and_bulk_update_guarded(self):
  ref=self.reviewed();self.drop=True;self.sales.command(self.body('confirm',ref,2,confirmed=True));row=self.s.db.query(Reserva).one()
  for statement in [text('DELETE FROM reservas WHERE id=:id'),text("UPDATE reservas SET escenario_parte_id=999 WHERE id=:id")]:
   with self.assertRaises(IntegrityError):
    with self.s.db.begin_nested():self.s.db.execute(statement,{'id':row.id});self.s.db.flush()
  self.assertEqual(self.s.db.query(Reserva).count(),1)
 def test_reversal_ack_releases_only_after_native_counterentry(self):
  ref=self.reviewed();r=self.sales.command(self.body('confirm',ref,2,confirmed=True));r=self.sales.command(self.body('review_reversal',ref,r['revision'],reason='Contrapartida revisada',support_digest='e'*64,confirmed=True));self.drop=True;r=self.sales.command(self.body('reverse',ref,r['revision'],confirmed=True));self.assertEqual(r['status'],'REVERSAL_PENDING');self.assertEqual(self.s.db.query(SaleSpaceClaim).filter_by(released=False).count(),1);r=self.sales.command(self.body('recover',ref,r['revision']));self.assertEqual(r['status'],'REVERSED');self.assertEqual(self.s.db.query(SaleSpaceClaim).filter_by(released=False).count(),0);self.assertEqual(self.s.db.query(Reserva).one().estado,'Cancelada');self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.n.base.tenant).count(),2)
 def test_expired_unposted_pending_can_cancel_and_re_review_same_sale(self):
  ref=self.reviewed()
  # Simulate a peer unavailable before applying the financial command.
  original=self.sales.bridge.rpc
  def unavailable(action,body,provider):
   if action=='command' and body['command']['operation']=='confirm':raise CRMError('SALE_LEDGER_RESULT_UNCERTAIN',503)
   return original(action,body,provider)
  self.sales.bridge.rpc=unavailable
  try:r=self.sales.command(self.body('confirm',ref,2,confirmed=True))
  finally:self.sales.bridge.rpc=original
  self.assertEqual(r['status'],'LEDGER_PENDING');self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.n.base.tenant).count(),0)
  with patch('apps.prestadores.mi_negocio.gestion_comercial.pool08.sales.datetime') as clock:
   clock.now.return_value=datetime.now(timezone.utc)+timedelta(minutes=16);expired=self.sales.command(self.body('recover',ref,r['revision']));self.assertTrue(expired['recovery_required']);self.assertEqual(expired['status'],'LEDGER_PENDING')
  r=expired
  r=self.sales.command(self.body('cancel',ref,r['revision'],reason='Revisión debe renovarse'));self.assertEqual(r['status'],'CANCELLED');self.assertEqual(self.s.db.query(SaleSpaceClaim).filter_by(released=False).count(),0)
  r=self.sales.command(self.body('review',ref,r['revision'],**self.n.terms('UNCONDITIONAL_RECEIVABLE')));r=self.sales.command(self.body('confirm',ref,r['revision'],confirmed=True));self.assertEqual(r['status'],'CONFIRMED');self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.n.base.tenant).count(),1);self.assertEqual(self.s.db.query(SaleSpaceClaim).filter_by(released=False).count(),1)
 def test_invalid_review_has_no_peer_side_effect(self):
  qid=self.quote();ref=self.sales.command(self.body(quotation_id=qid,provider_id=str(self.n.base.provider.pk)))['sale_id']
  with self.assertRaises(CRMError):self.sales.command(self.body('review',ref,1))
  self.assertIsNone(self.sales.get(ref).get('native_sale_id'));self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.n.base.tenant).count(),0)
if __name__=='__main__':unittest.main()
