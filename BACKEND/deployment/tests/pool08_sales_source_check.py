"""Reviewed SGA source ingress with actual native owner, journal and transaction.
Transport is in-process DRF; this suite does not qualify cross-server HTTP/TLS.
"""
import runpy,importlib,unittest,os,uuid,copy
from pathlib import Path
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_sales_native_check.py')),run_name='sales_source_fixture')
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent

def cases(system,path):
 api=importlib.import_module(path+'.source_api');protocol=importlib.import_module(path+'.source_protocol');bindings=importlib.import_module(path+'.source_binding');crm_api=importlib.import_module(path+'.crm_api');base=fixture['ERP' if system=='erp-tur' else 'Ana']
 class Checks(unittest.TestCase):
  def setUp(self):
   self.c=base();self.c.setUp();self.addCleanup(self.c.doCleanups);self.base=self.c.base
   self.env=patch.dict(os.environ,COMMERCIAL_SALES_SOURCE_KEY='synthetic-only-sale-source-key-more-than-32');self.env.start();self.addCleanup(self.env.stop)
   self.context={'system':'sga-cd','scope':'tenant:709','actor':'915','role_fingerprint':'f'*64,'issued_at':datetime.now(timezone.utc).isoformat()}
   self.binding=bindings.review_binding(operator=self.base.link.reviewed_by,provider_id=self.base.provider.pk,proof=protocol.wrap(self.context,{}),valid_until=datetime.now(timezone.utc)+timedelta(hours=1),support_digest='e'*64,apply=True)
   qid=self.c.q.create();self.c.q.issue(qid);link=self.c.q.link(qid);self.c.q.public(qid,link,self.c.q.acceptance(qid));quote=self.c.q.data(self.c.q.call(ref=qid));self.source={k:copy.deepcopy(quote[k]) for k in ('version','content_digest','content','acceptance')};self.source['quotation_id']=qid
   self.proof=dict(plan_digest='a'*64,valid=True,operation_refs=[],reserved=True,requires_capacity=False)
  def tearDown(self):self.c.tearDown()
  def call(self,action,body,context=None,signature=None,user=None):
   ctx={**self.context,'issued_at':datetime.now(timezone.utc).isoformat()} if context is None else context
   packet=protocol.wrap(ctx,body)
   if signature:packet['signature']=signature
   req=APIRequestFactory().post('/source/?provider_id='+str(self.base.provider.pk),packet,format='json');force_authenticate(req,user=user or self.base.user);return api.SaleSourceView.as_view()(req,action=action)
  def send(self,command,proof=None):return self.call('command',dict(command=command,source=self.source,operation_proof=proof or self.proof))
  def create(self):
   r=self.send(self.c.body(quotation_id=self.source['quotation_id']));self.assertEqual(r.status_code,200,r.data);return r.data['body']['sale']
  def test_signed_owner_mapping_actual_post_replay_and_reversal(self):
   sale=self.create();r=self.send(self.c.body('review',sale['id'],1,**self.c.terms()));self.assertEqual(r.status_code,200,r.data)
   command=self.c.body('confirm',sale['id'],2,confirmed=True);r=self.send(command);self.assertEqual(r.status_code,200,r.data);sale=r.data['body']['sale'];self.assertEqual(sale['status'],'CONFIRMED');self.assertTrue(JournalEntry.plain_objects.get(pk=sale['journal']['id']).is_posted)
   self.assertEqual(self.send(command).data['body']['sale']['journal'],sale['journal']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),1)
   self.assertEqual(self.send(self.c.body('review_reversal',sale['id'],3,reason='Revisión de contrapartida',support_digest='c'*64,confirmed=True)).status_code,200)
   r=self.send(self.c.body('reverse',sale['id'],4,confirmed=True));self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['body']['sale']['status'],'REVERSED');self.assertEqual(OutboxEvent.objects.filter(aggregate_root=sale['id']).count(),2)
  def test_unmapped_actor_wrong_role_and_other_native_owner_denied(self):
   for key,value in [('actor','916'),('role_fingerprint','1'*64),('scope','tenant:710')]:
    self.assertEqual(self.call('accounts',{},context={**self.context,key:value}).status_code,403)
   self.assertEqual(self.call('accounts',{},user=self.base.other).status_code,403)
  def test_signature_expiry_and_missing_key_fail_closed(self):
   self.assertEqual(self.call('accounts',{},signature='0'*64).status_code,403)
   self.assertEqual(self.call('accounts',{},context={**self.context,'issued_at':(datetime.now(timezone.utc)-timedelta(minutes=3)).isoformat()}).status_code,409)
   with patch.dict(os.environ,COMMERCIAL_SALES_SOURCE_KEY=''):
    with self.assertRaises(importlib.import_module(path+'.crm').CRMError):protocol.wrap(self.context,{})
  def test_source_cannot_bypass_review_through_native_sale_route(self):
   sale=self.create();r=self.c.call(self.c.body('review',sale['id'],1,**self.c.terms()));self.assertEqual(r.status_code,409,r.data)
  def test_tampered_source_and_malformed_acceptance_rejected(self):
   for change in ['digest','acceptance']:
    source=copy.deepcopy(self.source)
    if change=='digest':source['content']['title']='Alterada'
    else:source['acceptance']=None
    r=self.call('command',dict(command=self.c.body(quotation_id=source['quotation_id']),source=source,operation_proof=self.proof));self.assertEqual(r.status_code,422,r.data)
  def test_missing_durable_source_claim_prevents_post(self):
   sale=self.create();proof={**self.proof,'requires_capacity':True,'reserved':False};r=self.send(self.c.body('review',sale['id'],1,**self.c.terms()),proof);self.assertEqual(r.status_code,200,r.data)
   r=self.send(self.c.body('confirm',sale['id'],2,confirmed=True),proof);self.assertEqual(r.status_code,409,r.data);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),0)
  def test_binding_renewal_and_revocation_require_independent_cas_review(self):
   old=bindings.digest(bindings.binding_snapshot(self.binding));kw=dict(operator=self.base.link.reviewed_by,binding_id=self.binding.pk,proof=protocol.wrap(self.context,{}),expected_digest=old,valid_until=datetime.now(timezone.utc)+timedelta(hours=2),support_digest='c'*64,apply=True)
   updated=bindings.revise_binding(**kw);self.assertEqual(updated.pk,self.binding.pk);self.assertEqual(self.call('accounts',{}).status_code,200)
   with self.assertRaises(importlib.import_module(path+'.crm').CRMError):bindings.revise_binding(**kw)
   kw.update(expected_digest=bindings.digest(bindings.binding_snapshot(updated)),revoke=True);bindings.revise_binding(**kw);self.assertEqual(self.call('accounts',{}).status_code,403)
  def test_revoked_binding_and_self_review_blocked(self):
   with self.assertRaises(importlib.import_module(path+'.crm').CRMError):bindings.review_binding(operator=self.base.user,provider_id=self.base.provider.pk,proof=protocol.wrap(self.context,{}),valid_until=datetime.now(timezone.utc)+timedelta(hours=1),support_digest='a'*64,apply=True)
   self.binding.revoked_at=datetime.now(timezone.utc);self.binding.save();self.assertEqual(self.call('accounts',{}).status_code,403)
 Checks.__name__=system.replace('-','_')+'SaleSource';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
