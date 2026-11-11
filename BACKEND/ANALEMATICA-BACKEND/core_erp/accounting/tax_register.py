"""Read-only attribution of actual tax-account movements across reviewed sources.
No net tax declaration, inferred deductibility or comparison with tax authorities.
"""
from datetime import date
from decimal import Decimal,localcontext
from uuid import UUID
from django.db import transaction
from .models import Account,LedgerEntry
from .validation import lock_company
from .exceptions import AccountingError
from .reports_engine import ReportsEngine
from .tax_register_snapshot import load as load_snapshot
from .tax_explanation import references as policy_references

@transaction.atomic
def reconcile_tax_register(company_id,*,account_id,since,until):
    company=lock_company(company_id)
    start,end=date.fromisoformat(since),date.fromisoformat(until)
    if start.isoformat()!=since or end.isoformat()!=until or start>end or (end-start).days>366 or company.currency!='COP':raise AccountingError('Bounded canonical COP interval required.')
    account=Account.plain_objects.filter(pk=UUID(str(account_id)),tenant=company,chart_of_accounts__tenant=company,type__in=['ASSET','LIABILITY'],is_active=True).first()
    if account is None:raise AccountingError('Select an active scoped asset or liability tax account.')
    ReportsEngine.get_trial_balance(company.pk,end)
    movement=list(LedgerEntry.plain_objects.filter(tenant=company,account=account,journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__date__gte=start,journal_entry__date__lte=end).select_related('journal_entry').order_by('journal_entry__date','journal_entry_id','pk')[:2001])
    if len(movement)>2000:raise AccountingError('Narrow the interval; at most2000 account movements are supported.')
    groups={}
    for line in movement:groups.setdefault(line.journal_entry_id,[]).append(line)
    if len(groups)>250:raise AccountingError('Narrow the interval; at most250 journals are supported.')
    heads,all_lines,commercial_bodies,reservations=load_snapshot(company,groups)
    result=[];debit=credit=attributed=Decimal('0.00');totals={k:Decimal('0.00') for k in ['INPUT_TAX','OUTPUT_TAX','WITHHOLDING']};unattributed_groups=0
    policy_cache={};reference_count=0
    factor=Decimal(1) if account.type=='ASSET' else Decimal(-1)
    with localcontext() as context:
        context.prec=38
        for identifier,lines in groups.items():
            journal=heads[identifier]
            left=sum((l.debit_amount for l in lines),Decimal(0));right=sum((l.credit_amount for l in lines),Decimal(0));debit+=left;credit+=right
            tax={k:Decimal('0.00') for k in totals};document=reservation=None
            classification='UNATTRIBUTED_REQUIRES_REVIEW'
            original=heads.get(journal.reversed_entry_id) if journal.is_reversal else journal
            if original is None or original.is_reversal:raise AccountingError('Reversal original is unavailable.')
            body=commercial_bodies.get(str(original.pk));known_commercial=original.financial_event_id.startswith('commercial-tax:') if original.financial_event_id else False
            if known_commercial and body is None:raise AccountingError('Commercial origin proof missing; do not silently classify as manual.')
            if body:
                if journal.is_reversal:
                    actual=sorted((str(l.account_id),format(l.debit_amount,'.2f'),format(l.credit_amount,'.2f')) for l in all_lines[journal.pk])
                    expected=sorted((r['account_id'],r['credit'],r['debit']) for r in body['preview']['lines'])
                    if actual!=expected:raise AccountingError('Reversal differs from exact reviewed contra entries.')
                sign=Decimal(-1) if journal.is_reversal else Decimal(1)
                for row in body['preview']['lines']:
                    if row['account_id']==str(account.pk) and row['kind'] in tax:
                        tax[row['kind']]+=(Decimal(row['debit'])-Decimal(row['credit']))*factor*sign
                if any(tax.values()):document=body['document_id'];classification='REVIEWED_COMMERCIAL_TAX'
            if str(original.pk) in reservations:
                if body:raise AccountingError('Conflicting reservation/commercial attribution.')
                source,reviewed=reservations[str(original.pk)]
                if reviewed.get('account_mapping',{}).get('tax_liability')==str(account.pk):
                    amount=Decimal(reviewed['totals']['tax']);expected=(amount,Decimal(0)) if journal.is_reversal else (Decimal(0),amount)
                    if (left,right)!=expected:raise AccountingError('Tax amount differs from reviewed reservation.')
                    tax['OUTPUT_TAX']=(left-right)*factor
                    reservation=source['reservation_id'];classification='REVIEWED_RESERVATION_TAX'
            normal=(left-right)*factor;covered=sum(tax.values(),Decimal(0));unattributed=normal-covered
            if unattributed or classification=='UNATTRIBUTED_REQUIRES_REVIEW':unattributed_groups+=1
            attributed+=covered
            for kind,value in tax.items():totals[kind]+=value
            refs=policy_references(company,body,policy_cache) if body else []
            reference_count+=len(refs)
            if reference_count>500:raise AccountingError('Narrow the interval; at most500 policy references are supported, never truncated.')
            result.append({'journal_id':str(journal.pk),'date':journal.date.isoformat(),'journal_hash':journal.system_hash,'is_reversal':journal.is_reversal,'debit':format(left,'.2f'),'credit':format(right,'.2f'),'normal_movement':format(normal,'.2f'),'tax_by_kind':{k:format(v,'.2f') for k,v in tax.items()},'unattributed_normal_movement':format(unattributed,'.2f'),'classification':classification,'document_id':document,'reservation_id':reservation,'policy_references':refs,'policy_coverage':'ORIGINAL_VERSION_REFERENCED' if body and ('fact' in body or 'tax_source' in body) else 'NOT_CAPTURED_IN_SOURCE'})
        normal=(debit-credit)*factor
        return {'schema':'sgacd-tax-register-v3','company_id':str(company.pk),'tenant_id':str(company.pk),'account_id':str(account.pk),'account_code':account.code,'account_type':account.type,'normal_side':'DEBIT' if account.type=='ASSET' else 'CREDIT','since':since,'until':until,'currency':'COP','read_only':True,'posted_only':True,'valuation':'base_currency','debit':format(debit,'.2f'),'credit':format(credit,'.2f'),'normal_movement':format(normal,'.2f'),'attributed_normal_movement':format(attributed,'.2f'),'tax_by_kind':{k:format(v,'.2f') for k,v in totals.items()},'unattributed_normal_movement':format(normal-attributed,'.2f'),'unattributed_journals':unattributed_groups,'lines':result,'ledger_written':False,'dian_compared':False,'fiscal_accepted':False,'regulatory_verified':False,'scope':'SELECTED_ACCOUNT_MOVEMENTS_NOT_A_TAX_RETURN'}
