"""Bounded tax-account reconciliation against actual reservation journal evidence.

No inferred tax rates, no declaration, no DIAN comparison or acceptance. The owner
selects the liability account; manual/unattributed movements remain explicit.
"""
from datetime import date
from decimal import Decimal,localcontext
from uuid import UUID
from django.db import transaction
from .models import Account,JournalEntry,LedgerEntry
from .validation import lock_company
from .exceptions import AccountingError
from .integrity import fingerprint
from .reports_engine import ReportsEngine
from apps.core_erp.outbox_models import OutboxEvent

@transaction.atomic
def reconcile_tax_account(company_id,*,account_id,since,until):
    company=lock_company(company_id)
    start=date.fromisoformat(since);end=date.fromisoformat(until)
    if start.isoformat()!=since or end.isoformat()!=until or start>end or (end-start).days>366:raise AccountingError('Invalid reconciliation interval.')
    if company.currency!='COP':raise AccountingError('COP-only reconciliation; no implicit currency conversion.')
    account=Account.plain_objects.filter(pk=UUID(str(account_id)),tenant=company,chart_of_accounts__tenant=company,type='LIABILITY',is_active=True).first()
    if account is None:raise AccountingError('Select an active reviewed liability account of this company.')
    # Preserve shared opening/valuation checks, including other account groups.
    ReportsEngine.get_trial_balance(company.pk,end)
    rows=list(LedgerEntry.plain_objects.filter(tenant=company,account=account,journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__date__gte=start,journal_entry__date__lte=end).select_related('journal_entry').order_by('journal_entry__date','journal_entry_id','pk')[:2001])
    if len(rows)>2000:raise AccountingError('Narrow the interval; reconciliation exceeds 2000 tax-account movements.')
    journals={row.journal_entry_id:row.journal_entry for row in rows}
    originals={journal.reversed_entry_id for journal in journals.values() if journal.is_reversal}
    source_ids={str(identifier) for identifier in set(journals)|originals if identifier}
    proofs=list(OutboxEvent.objects.filter(event_type='accounting.reservation.recognized.v1',payload__company_id=str(company.pk),payload__journal_id__in=source_ids)[:2001])
    if len(proofs)>2000:raise AccountingError('Too many source proofs.')
    by_journal={}
    for proof in proofs:
        identifier=proof.payload.get('journal_id')
        if identifier in by_journal:raise AccountingError('Conflicting source evidence.')
        by_journal[identifier]=proof
    review_ids=[proof.payload.get('review_id') for proof in proofs]
    reviews={str(row.pk):row for row in OutboxEvent.objects.filter(pk__in=review_ids,event_type='accounting.reservation.recognition-reviewed.v1',payload__company_id=str(company.pk))}
    result=[];debits=Decimal(0);credits=Decimal(0);attributed=Decimal(0)
    with localcontext() as ctx:
        ctx.prec=38
        for row in rows:
            journal=row.journal_entry
            if row.currency!='COP' or journal.base_currency!='COP' or journal.hash_version!='v2' or journal.compute_hash()!=journal.system_hash:raise AccountingError('Journal needs integrity/currency reconciliation.')
            debits+=row.debit_amount;credits+=row.credit_amount
            original_id=journal.reversed_entry_id if journal.is_reversal else journal.pk
            proof=by_journal.get(str(original_id));source=None;policies=[]
            if proof:
                review=reviews.get(proof.payload.get('review_id'));body=review.payload.get('review') if review else None
                if not isinstance(body,dict) or fingerprint(body)!=review.payload.get('review_digest') or review.payload.get('review_digest')!=proof.payload.get('review_digest') or body.get('company_id')!=str(company.pk):raise AccountingError('Reviewed tax evidence is inconsistent.')
                original=journal if not journal.is_reversal else JournalEntry.plain_objects.filter(pk=original_id,tenant=company,is_posted=True).first()
                if original is None or original.compute_hash()!=original.system_hash or original.system_hash!=proof.payload.get('journal_hash'):raise AccountingError('Source journal evidence is inconsistent.')
                if body.get('account_mapping',{}).get('tax_liability')==str(account.pk):
                    tax=Decimal(body['totals']['tax'])
                    if (row.debit_amount,row.credit_amount)!=((tax,Decimal(0)) if journal.is_reversal else (Decimal(0),tax)):raise AccountingError('Tax amount differs from reviewed recognition.')
                    source=proof.payload.get('reservation_id');attributed+=row.credit_amount-row.debit_amount
            result.append({'journal_id':str(journal.pk),'date':journal.date.isoformat(),'debit':format(row.debit_amount,'.2f'),'credit':format(row.credit_amount,'.2f'),'is_reversal':journal.is_reversal,'reservation_id':source,'classification':'REVIEWED_RESERVATION_TAX' if source else 'UNATTRIBUTED_REQUIRES_REVIEW','journal_hash':journal.system_hash})
        net=credits-debits
        return {'schema':'sgacd-tax-reconciliation-v1','tenant_id':str(company.pk),'company_id':str(company.pk),'account_id':str(account.pk),'account_code':account.code,'since':since,'until':until,'currency':'COP','read_only':True,'posted_only':True,'valuation':'base_currency','debit':format(debits,'.2f'),'credit':format(credits,'.2f'),'net_liability_movement':format(net,'.2f'),'reviewed_reservation_tax':format(attributed,'.2f'),'unattributed_net':format(net-attributed,'.2f'),'unattributed_movements':sum(row['reservation_id'] is None for row in result),'lines':result,'tax_policy_verified':False,'dian_compared':False,'fiscal_accepted':False,'ledger_written':False}
