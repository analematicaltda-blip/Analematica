"""Controlled draft source correction, immutable capture and stale payroll rejection."""
import copy,runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
f=runpy.run_path(str(Path(__file__).with_name('accounting_native_payroll_source_check.py')),run_name='native_correction_fixture')
engine=f['engine'];payroll=f['payroll'];OutboxEvent=f['OutboxEvent'];NovedadNomina=f['NovedadNomina'];AccountingError=f['AccountingError']
class CorrectionChecks(unittest.TestCase):
 def setUp(self):
  self.b=f['NativeSourceChecks']();self.b.setUp();self.capture=self.b.record();self.args={'actor':self.b.base.owner,'provider_id':self.b.base.provider.pk,'payroll_id':str(self.b.base.payroll.pk),'novelty_id':self.capture['novelty_id'],'request_id':str(uuid.uuid4()),'expected_revision':0,'event_date':self.b.base.day.isoformat(),'amount':'60.00','reason_code':'DATA_ENTRY_ERROR','evidence_digest':'c'*64,'authorization_digest':'d'*64,'confirmed':True}
 def correct(self,**kw):return engine.correct(**{**self.args,**kw})
 def test_original_preserved_and_history_recovers_effective_source(self):
  original=copy.deepcopy(OutboxEvent.objects.get(pk=engine.key('record',self.b.base.company,self.b.args['request_id'])).payload);r=self.correct();self.assertEqual(r['revision'],1);self.assertEqual(r['source']['amount'],'60.00');self.assertEqual(r['history'][0]['before']['amount'],'50.00');self.assertFalse(r['ledger_written']);self.assertFalse(r['money_transferred']);self.assertEqual(self.b.lookup()['history_digest'],r['history_digest']);self.assertEqual(OutboxEvent.objects.get(pk=engine.key('record',self.b.base.company,self.b.args['request_id'])).payload,original)
 def test_request_replay_and_conflict(self):
  a=self.correct();b=self.correct();self.assertTrue(b['replayed']);self.assertFalse(b['metadata_written']);self.assertEqual(a['history_digest'],b['history_digest'])
  with self.assertRaises(AccountingError):self.correct(amount='61.00')
  with self.assertRaises(AccountingError):self.correct(request_id=str(uuid.uuid4()))
 def test_later_correction_requires_latest_revision(self):
  self.correct();r=self.correct(request_id=str(uuid.uuid4()),expected_revision=1,amount='70.00');self.assertEqual(r['revision'],2);self.assertEqual(len(r['history']),2)
  with self.assertRaises(AccountingError):self.correct()
  with self.assertRaises(AccountingError):self.b.record()
 def test_audit_failure_rolls_back_amount_and_can_retry(self):
  create=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==engine.CORRECTED:raise RuntimeError('Synthetic correction proof failure')
   return create(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.correct()
  self.assertEqual(self.b.lookup()['source']['amount'],'50.00');self.assertEqual(self.b.lookup()['revision'],0);self.correct()
 def test_support_only_correction_tail_cannot_disappear(self):
  self.correct(amount='50.00');OutboxEvent.objects.filter(event_type=engine.CORRECTED,aggregate_root=str(self.capture['novelty_id'])).delete()
  with self.assertRaises(AccountingError):self.b.lookup()
 def test_changed_chain_or_missing_head_blocks_recovery(self):
  self.correct();OutboxEvent.objects.filter(pk=engine.key('correction-head',self.b.base.company,self.capture['novelty_id'])).delete()
  with self.assertRaises(AccountingError):self.b.lookup()
 def test_source_tampering_after_correction_rejected(self):
  self.correct();NovedadNomina.objects.filter(pk=self.capture['novelty_id']).update(valor='61.00')
  with self.assertRaises(AccountingError):self.b.lookup()
 def test_validation_rejects_false_review_precision_revision_and_zero(self):
  for kw in [{'confirmed':False},{'expected_revision':True},{'novelty_id':True},{'expected_revision':-1},{'amount':'0.00'},{'amount':'60.001'},{'amount':60.0},{'reason_code':'OTHER'},{'evidence_digest':'bad'},{'event_date':'1990-01-01'}]:
   with self.assertRaises((AccountingError,ValueError)):self.correct(**kw)
  self.assertEqual(self.b.lookup()['revision'],0)
 def test_noop_is_not_new_history(self):
  with self.assertRaises(AccountingError):self.correct(amount='50.00',evidence_digest='a'*64,authorization_digest='b'*64)
 def test_old_review_rejected_then_new_review_posts_corrected_amount_once(self):
  old=self.b.review(self.capture);self.correct()
  with self.assertRaises(AccountingError):self.b.base.post(old)
  self.b.args.update(evidence_digest='c'*64,authorization_digest='d'*64);new=self.b.review(self.b.lookup(),expected_revision=1);self.assertEqual(new['preview']['snapshot']['totals']['gross'],'560.00');posted=self.b.base.post(new);self.assertEqual(self.b.base.post(new)['journal_id'],posted['journal_id']);self.assertTrue(self.b.lookup()['processed'])
  with self.assertRaises(AccountingError):self.correct(request_id=str(uuid.uuid4()),expected_revision=1,amount='70.00')
 def test_old_support_references_cannot_review_corrected_source(self):
  self.correct()
  with self.assertRaises(AccountingError):self.b.review(self.capture)
 def test_support_only_correction_invalidates_old_payroll_review(self):
  old=self.b.review(self.capture);self.correct(amount='50.00')
  with self.assertRaises(AccountingError):self.b.base.post(old)
 def test_date_correction_inside_period_preserves_original_date(self):
  from datetime import timedelta
  day=max(self.b.base.start,self.b.base.day-timedelta(days=1));r=self.correct(event_date=day.isoformat());self.assertEqual(r['source']['date'],day.isoformat());self.assertEqual(r['history'][0]['before']['date'],self.b.base.day.isoformat())
 def test_other_payroll_cannot_correct_original_source(self):
  other=f['Planilla'].objects.create(perfil_id=self.b.base.provider.pk,periodo_inicio=self.b.base.start,periodo_fin=self.b.base.day)
  with self.assertRaises(AccountingError):self.correct(payroll_id=str(other.pk))
 def test_head_write_failure_rolls_back_source_and_proof(self):
  with patch.object(OutboxEvent.objects,'update_or_create',side_effect=RuntimeError('Synthetic head failure')):
   with self.assertRaises(RuntimeError):self.correct()
  self.assertEqual(self.b.lookup()['revision'],0);self.assertEqual(self.b.lookup()['source']['amount'],'50.00');self.assertFalse(OutboxEvent.objects.filter(event_type=engine.CORRECTED,aggregate_root=str(self.capture['novelty_id'])).exists())
 def test_strict_api_and_corporate_response_contract(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  payload={k:v for k,v in self.args.items() if k not in ['actor','provider_id']}
  def call(data):
   req=APIRequestFactory().post('/fixture/?provider_id='+str(self.b.base.provider.pk),data,format='json');force_authenticate(req,user=self.b.base.owner);return PlanCuentaViewSet.as_view({'post':'correct_native_payroll_novelty'})(req)
  self.assertEqual(call({**payload,'employee_id':str(uuid.uuid4())}).status_code,400);r=call(payload);self.assertEqual(r.status_code,200,r.data)
  import sys
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
  from app.services.native_payroll_source_contract import validate
  validate('correct_native_payroll_novelty',r.data,payload,{'tenant_id':str(self.b.base.company.pk)})
  for change in [{'revision':5},{'correction_request_id':str(uuid.uuid4())},{'metadata_written':False}]:
   with self.assertRaises(ValueError):validate('correct_native_payroll_novelty',{**r.data,**change},payload,{'tenant_id':str(self.b.base.company.pk)})
if __name__=='__main__':unittest.main()
