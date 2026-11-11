"""Synthetic history for real HTTP read qualification; never production data."""
def seed(case,count=2001):
 from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
 from apps.core_erp.accounting.integrity import journal_hash
 from django.utils import timezone
 from datetime import timedelta
 from decimal import Decimal
 import uuid
 prior=timezone.localdate()-timedelta(days=1);case.period.period_start=prior;case.period.save();journals=[];lines=[]
 for _ in range(count):
  j=JournalEntry(id=uuid.uuid4(),tenant=case.tenant,period=case.period,date=prior,reference='SYNTHETIC-HISTORY',description='Synthetic history read fixture',currency='COP',base_currency='COP',exchange_rate=Decimal(1),is_posted=True,hash_version='v2',posted_at=timezone.now(),created_by=case.user,previous_hash=None)
  pair=[LedgerEntry(id=uuid.uuid4(),tenant=case.tenant,journal_entry=j,account=account,debit_amount=Decimal(1) if debit else Decimal(0),credit_amount=Decimal(0) if debit else Decimal(1),amount_transaction=Decimal(1),amount_base=Decimal(1),currency='COP') for account,debit in [(case.a,True),(case.b,False)]]
  j.system_hash=journal_hash(j,pair,None);journals.append(j);lines+=pair
 JournalEntry.plain_objects.bulk_create(journals,batch_size=100);LedgerEntry.plain_objects.bulk_create(lines,batch_size=100)
