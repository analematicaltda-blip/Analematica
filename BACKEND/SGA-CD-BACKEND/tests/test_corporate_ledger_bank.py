"""Real authenticated corporate/ERP matching and append-only release, disposable data."""
import hashlib,unittest
import test_corporate_ledger_integration as integration
class CorporateBankTests(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 setUp=integration.DualLedgerIntegration.setUp
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def bank_source(self):
  p=self.unwrap(self.erp.get(integration.bridge.BASE+'clasificacion-liquidez/',params={'provider_id':self.provider}).json())
  return p['mapping']['cash_equivalents'][0],'transaction_id,date,direction,amount,currency\nprivate-bank-001,'+self.day+',IN,10.00,COP\n'
 def test_actual_compare_confirm_recover_release_no_ledger_mutation(self):
  account,text=self.bank_source();comparison=self.command('compare_bank_statement',{'account_id':account,'csv_text':text});self.assertEqual(comparison.status_code,200,comparison.text);self.assertFalse(comparison.json()['data']['bank_verified'])
  review=self.command('review_bank_reconciliation',{'account_id':account,'csv_text':text,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True});self.assertEqual(review.status_code,200,review.text)
  args={'statement_id':review.json()['data']['statement_id'],'review_id':review.json()['data']['review_id'],'confirmed':False};self.assertEqual(self.command('confirm_bank_reconciliation',args).status_code,422)
  args['confirmed']=True;confirmed=self.command('confirm_bank_reconciliation',args);self.assertEqual(confirmed.status_code,200,confirmed.text);result=confirmed.json()['data'];self.assertTrue(result['reconciliation_confirmed']);self.assertFalse(result['ledger_written']);self.assertTrue(self.command('confirm_bank_reconciliation',args).json()['data']['replayed'])
  state=self.client.get('/api/v1/workspace/corporate/accounting/sources/bank_reconciliation_state',params={'account_id':account,'source_digest':hashlib.sha256(text.encode()).hexdigest()});self.assertEqual(state.status_code,200,state.text);self.assertEqual(state.json()['applied']['reconciliation_id'],result['reconciliation_id']);self.assertFalse(state.json()['confirmations_restored']);self.assertNotIn('private-bank-001',state.text)
  release=self.command('review_bank_release',{'reconciliation_id':result['reconciliation_id'],'reason_code':'WRONG_MATCH','evidence_digest':'b'*64,'confirmed':True});self.assertEqual(release.status_code,200,release.text)
  r={'review_id':release.json()['data']['review_id'],'confirmed':False};self.assertEqual(self.command('confirm_bank_release',r).status_code,422);r['confirmed']=True
  released=self.command('confirm_bank_release',r);self.assertEqual(released.status_code,200,released.text);self.assertTrue(released.json()['data']['released']);self.assertFalse(released.json()['data']['money_transferred'])
  report=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'trial_balance','until':self.day});self.assertEqual(report.status_code,200,report.text);self.assertEqual(report.json()['data']['total_debit'],'15.00')
 def test_another_source_cannot_reuse_an_active_ledger_line(self):
  account,text=self.bank_source();payload={'account_id':account,'csv_text':text,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True};review=self.command('review_bank_reconciliation',payload).json()['data'];r=self.command('confirm_bank_reconciliation',{'statement_id':review['statement_id'],'review_id':review['review_id'],'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  payload['csv_text']=text.replace('private-bank-001','different-bank-reference');blocked=self.command('review_bank_reconciliation',payload);self.assertEqual(blocked.status_code,409,blocked.text)
 def test_partial_statement_preserves_unresolved_amount_and_reserves_reference(self):
  account,text=self.bank_source();text+='private-fee-002,'+self.day+',OUT,2.00,COP\n'
  compare=self.command('compare_bank_statement',{'account_id':account,'csv_text':text});self.assertEqual(compare.status_code,200,compare.text);line=compare.json()['data']['rows'][0]['candidates'][0]['ledger_line_id']
  decisions=[{'row':1,'ledger_line_id':line,'reason_code':None},{'row':2,'ledger_line_id':None,'reason_code':'BANK_FEE_UNPOSTED'}]
  payload={'account_id':account,'csv_text':text,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True,'resolutions':decisions};review=self.command('review_bank_reconciliation',payload);self.assertEqual(review.status_code,200,review.text);r=review.json()['data'];self.assertEqual(r['preview']['coverage']['unresolved_out'],'2.00')
  posted=self.command('confirm_bank_reconciliation',{'statement_id':r['statement_id'],'review_id':r['review_id'],'confirmed':True});self.assertEqual(posted.status_code,200,posted.text);a=posted.json()['data'];self.assertTrue(a['associations_confirmed']);self.assertFalse(a['fully_reconciled']);self.assertFalse(a['reconciliation_confirmed']);self.assertFalse(a['ledger_written'])
  state=self.client.get('/api/v1/workspace/corporate/accounting/sources/bank_reconciliation_state',params={'account_id':account,'source_digest':hashlib.sha256(text.encode()).hexdigest()});self.assertEqual(state.status_code,200,state.text);self.assertFalse(state.json()['confirmations_restored']);self.assertEqual(state.json()['preview']['differences'][0]['reason_code'],'BANK_FEE_UNPOSTED')
  replay=self.command('confirm_bank_reconciliation',{'statement_id':r['statement_id'],'review_id':r['review_id'],'confirmed':True});self.assertEqual(replay.json()['data']['reconciliation_id'],a['reconciliation_id']);self.assertTrue(replay.json()['data']['replayed']);self.assertNotIn('private-fee-002',state.text)
 def test_unexplained_difference_cannot_be_confirmed_through_corporate_bridge(self):
  account,text=self.bank_source();text+='private-fee-002,'+self.day+',OUT,2.00,COP\n';comparison=self.command('compare_bank_statement',{'account_id':account,'csv_text':text}).json()['data'];line=comparison['rows'][0]['candidates'][0]['ledger_line_id']
  payload={'account_id':account,'csv_text':text,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True,'resolutions':[{'row':1,'ledger_line_id':line,'reason_code':None},{'row':2,'ledger_line_id':None,'reason_code':'SILENTLY_IGNORE'}]};r=self.command('review_bank_reconciliation',payload);self.assertEqual(r.status_code,409,r.text);self.assertNotIn('review_id',r.text)
 def test_period_balances_and_full_cash_coverage_are_confirmed_and_recovered(self):
  account,text=self.bank_source();text+='private-funding-002,'+self.day+',IN,5.00,COP\n'
  terms={'since':self.day,'until':self.day,'opening':'0.00','closing':'15.00','statement_complete':True,'evidence_digest':'e'*64}
  review=self.command('review_bank_reconciliation',{'account_id':account,'csv_text':text,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True,'period':terms});self.assertEqual(review.status_code,200,review.text);r=review.json()['data'];a=r['preview']['period_assessment'];self.assertEqual(a['ledger_closing'],'15.00');self.assertTrue(a['eligible_for_period_reconciliation'])
  confirmed=self.command('confirm_bank_reconciliation',{'statement_id':r['statement_id'],'review_id':r['review_id'],'confirmed':True});self.assertEqual(confirmed.status_code,200,confirmed.text);p=confirmed.json()['data'];self.assertTrue(p['period_reconciled']);self.assertFalse(p['bank_verified']);self.assertFalse(p['money_transferred'])
  state=self.client.get('/api/v1/workspace/corporate/accounting/sources/bank_reconciliation_state',params={'account_id':account,'source_digest':hashlib.sha256(text.encode()).hexdigest()});self.assertEqual(state.status_code,200,state.text);self.assertTrue(state.json()['applied']['period_reconciled']);self.assertFalse(state.json()['confirmations_restored'])
if __name__=='__main__':unittest.main()
