"""ESG trace to declared operational origin and effective support, not certification."""
import runpy,unittest,copy
from pathlib import Path
from decimal import localcontext,Inexact,Rounded
f=runpy.run_path(str(Path(__file__).with_name('accounting_acc018_source_check.py')),run_name='acc019_source_fixture')
from django.utils import timezone
from apps.prestadores.mi_negocio.gestion_contable.contabilidad import esg_reporting as engine
from apps.core_erp.accounting.exceptions import AccountingError
class ESGTraceChecks(unittest.TestCase):
 def setUp(self):
  self.source=f['SourceChecks']();self.source.setUp();self.base=self.source.base;self.addCleanup(self.base.doCleanups);self.record=self.base.record(self.source.review());self.args={'actor':self.base.owner,'provider_id':self.base.provider.pk,'since':self.base.day,'until':self.base.day,'as_of':timezone.now().isoformat(),'mappings':{}}
 def report(self,**kwargs):return engine.report(**{**self.args,**kwargs})
 def test_operational_source_and_support_exported(self):
  row=self.report()['items'][0];self.assertEqual(row['source_reference'],str(self.source.order.pk));self.assertEqual(row['source_segment'],'OUTBOUND');self.assertEqual(len(row['activity_support_digest']),64)
 def test_decimal_context_does_not_change_report_or_leak(self):
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad import environmental_corrections as corrections
  args={'actor':self.base.owner,'provider_id':self.base.provider.pk,'observation_id':self.record['observation_id'],'confirmed':True}
  review=corrections.review_correction(**args,expected_revision=0,activities=[{**self.source.activity,'quantity':'100.000001'}],factors=[self.base.factor],evidence_digest='c'*64,reason_code='QUANTITY_ERROR');corrections.record_correction(**args,review_id=review['review_id']);self.args['as_of']=timezone.now().isoformat()
  expected=self.report()
  with localcontext() as ctx:
   ctx.prec=2;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True;self.assertEqual(self.report(),expected);self.assertEqual(ctx.prec,2)
 def test_nested_framework_type_rejected_as_domain_error(self):
  for value in [[],{},None,True]:
   with self.assertRaises(AccountingError):self.report(mappings={'direct_combustion':{'framework':value,'version':'2016','reference':'305-1','evidence_digest':'a'*64}})
 def test_correction_support_follows_knowledge_cut_and_retains_source(self):
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad import environmental_corrections as corrections
  original=self.report();args={'actor':self.base.owner,'provider_id':self.base.provider.pk,'observation_id':self.record['observation_id'],'confirmed':True}
  review=corrections.review_correction(**args,expected_revision=0,activities=[{**self.source.activity,'quantity':'200'}],factors=[self.base.factor],evidence_digest='c'*64,reason_code='QUANTITY_ERROR')
  corrections.record_correction(**args,review_id=review['review_id'])
  self.assertEqual(self.report(),original)
  corrected=self.report(as_of=timezone.now().isoformat());row=corrected['items'][0];self.assertEqual(row['activity_support_digest'],'c'*64);self.assertEqual(row['source_reference'],str(self.source.order.pk));self.assertEqual(row['revision'],1);self.assertEqual(corrected['activity_count'],1);self.assertEqual(corrected['totals_by_boundary']['direct_combustion'],'24.691200')
 def test_source_claim_loss_prevents_export(self):
  from apps.core_erp.outbox_models import OutboxEvent
  OutboxEvent.objects.filter(event_type=f['engine'].SOURCE).delete()
  with self.assertRaises(AccountingError):self.report()
if __name__=='__main__':unittest.main(verbosity=2)
