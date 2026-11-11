"""55 synthetic confirmations before serving HTTP; preserves request quotas."""
def seed(case):
 from uuid import uuid4
 from django.utils import timezone
 from apps.core_erp.accounting import bank_grouped as groups
 day=timezone.localdate().isoformat();account=str(case.a.pk)
 def text(i):return 'transaction_id,date,direction,amount,currency\npage-browser-'+str(i)+','+day+',IN,0.01,COP\n'
 source=groups.sources(case.tenant.pk,actor=case.user,account_id=account,csv_text=text(0))
 line=next(r for r in source['ledger_lines'] if r['direction']=='IN' and r['amount']=='10.00')
 for i in range(55):
  review=groups.review(case.tenant.pk,actor=case.user,account_id=account,csv_text=text(i),groups=[{'group_id':str(uuid4()),'bank_rows':[1],'ledger_allocations':[{'ledger_line_id':line['ledger_line_id'],'amount':'0.01'}]}],evidence_digest='a'*64,expected_revision=0,confirmed=True)
  groups.confirm(case.tenant.pk,actor=case.user,statement_id=review['statement_id'],review_id=review['review_id'],confirmed=True)
