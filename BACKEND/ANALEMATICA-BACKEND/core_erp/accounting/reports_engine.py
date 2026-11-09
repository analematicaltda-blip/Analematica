"""Read-only base-currency reports from posted, explicitly company-scoped lines."""
from decimal import Decimal
from django.db.models import Sum,Case,When,F,Value,DecimalField,Q
from .models import LedgerEntry, Account
from .exceptions import AccountingError

from functools import wraps
from inspect import signature
from datetime import date
from decimal import localcontext
from django.db import transaction
from .validation import lock_company
from .models import JournalEntry

def financial_snapshot(function):
    contract=signature(function)
    @wraps(function)
    def coherent(*args,**kwargs):
        params=contract.bind(*args,**kwargs).arguments
        cutoff=params.get('cutoff_date',params.get('end_date'));start=params.get('start_date')
        if type(cutoff) is not date or (start is not None and (type(start) is not date or start>cutoff)):raise AccountingError('Invalid economic-date interval.')
        with transaction.atomic(),localcontext() as ctx:
            ctx.prec=38
            company=lock_company(params['tenant_id'])
            headers=JournalEntry.plain_objects.filter(tenant=company,is_posted=True,date__lte=cutoff)
            if start is not None:headers=headers.filter(date__gte=start)
            if headers.exclude(base_currency=company.currency).exists():raise AccountingError('Historical base currencies require reconciliation.')
            result=function(*args,**kwargs)
            tail=JournalEntry.plain_objects.filter(tenant=company,is_posted=True).order_by('-posted_at','-pk').first()
            result['snapshot']={'database':'primary','consistency':'company_lock_shared_with_posting','ledger_tail_id':str(tail.pk) if tail else None,'ledger_tail_hash':tail.system_hash if tail else None,'historical_publication_snapshot':False}
            result.setdefault('tenant_id',str(company.pk));result.setdefault('currency',company.currency)
            return result
    return coherent

ZERO=Decimal('0.00')

class ReportsEngine:
    @staticmethod
    def get_read_db():
        from django.conf import settings
        return 'read_replica' if 'read_replica' in settings.DATABASES else 'default'

    @staticmethod
    def _totals(tenant_id,cutoff_date,start_date=None,*,database=None,account_types=None):
        allowed_types={'ASSET','LIABILITY','EQUITY','REVENUE','EXPENSE','COST_OF_SALES','PRODUCTION_COST','DEBTOR_ORDER','CREDITOR_ORDER'}
        if account_types is not None and (not isinstance(account_types,(tuple,list)) or not account_types
                or any(not isinstance(kind,str) or kind not in allowed_types for kind in account_types)):
            raise AccountingError('Explicit supported account types required.')
        database=database or ReportsEngine.get_read_db()
        if not tenant_id:raise AccountingError('An explicit reporting company is required.')
        if database=='default':
            from .opening_balances import inspect_opening
            inspect_opening(tenant_id,cutoff_date)
        elif Account.plain_objects.using(database).filter(tenant_id=tenant_id).exclude(initial_balance=0).exists():
            raise AccountingError('Opening reconciliation requires authoritative primary reporting.')
        query=LedgerEntry.plain_objects.using(database).filter(
            tenant_id=tenant_id,journal_entry__tenant_id=tenant_id,account__tenant_id=tenant_id,
            journal_entry__is_posted=True,journal_entry__date__lte=cutoff_date)
        if start_date:query=query.filter(journal_entry__date__gte=start_date)
        if query.exclude(journal_entry__currency=F('journal_entry__base_currency')).filter(amount_base__lte=0).exists():
            raise AccountingError('Legacy foreign-currency valuation requires reconciliation.')
        # Apply only after company-wide legacy/valuation checks, never hide unsafe rows.
        if account_types is not None:query=query.filter(account__type__in=sorted(set(account_types)))
        value=Case(When(journal_entry__currency=F('journal_entry__base_currency'),then=F('debit_amount')+F('credit_amount')),
                   default=F('amount_base'),output_field=DecimalField(max_digits=28,decimal_places=2))
        debit=Case(When(debit_amount__gt=0,then=value),default=Value(ZERO),output_field=DecimalField(max_digits=28,decimal_places=2))
        credit=Case(When(credit_amount__gt=0,then=value),default=Value(ZERO),output_field=DecimalField(max_digits=28,decimal_places=2))
        return list(query.values('account_id','account__code','account__name','account__type').annotate(
            debit=Sum(debit),credit=Sum(credit)).order_by('account__code','account_id'))

    @staticmethod
    @financial_snapshot
    def get_trial_balance(tenant_id,cutoff_date):
        values=ReportsEngine._totals(tenant_id,cutoff_date,database='default')
        lines=[]
        for row in values:
            debit=(row['debit'] or ZERO).quantize(Decimal('0.01'));credit=(row['credit'] or ZERO).quantize(Decimal('0.01'))
            balance=debit-credit if row['account__type'] in {'ASSET','EXPENSE','COST_OF_SALES','PRODUCTION_COST','DEBTOR_ORDER'} else credit-debit
            lines.append({'account_code':row['account__code'],'account_name':row['account__name'],'debit':debit,'credit':credit,'balance':balance})
        return {'tenant_id':tenant_id,'cutoff_date':cutoff_date,'lines':lines,
                'total_debit':sum((r['debit'] for r in lines),ZERO),'total_credit':sum((r['credit'] for r in lines),ZERO),
                'valuation':'base_currency','posted_only':True}

    @staticmethod
    @financial_snapshot
    def get_p_and_l(tenant_id,start_date,end_date):
        income=expenses=ZERO
        for row in ReportsEngine._totals(tenant_id,end_date,start_date,database='default'):
            if row['account__type']=='REVENUE':income+=row['credit']-row['debit']
            elif row['account__type'] in {'EXPENSE','COST_OF_SALES','PRODUCTION_COST'}:expenses+=row['debit']-row['credit']
        return {'income':income,'expenses':expenses,'net_profit':income-expenses}

    @staticmethod
    @financial_snapshot
    def get_balance_sheet(tenant_id,cutoff_date):
        totals={key:ZERO for key in ['ASSET','LIABILITY','EQUITY','REVENUE','EXPENSE','COST_OF_SALES','PRODUCTION_COST']}
        for row in ReportsEngine._totals(tenant_id,cutoff_date,database='default'):
            kind=row['account__type']
            if kind in totals:
                totals[kind]+=row['debit']-row['credit'] if kind in {'ASSET','EXPENSE','COST_OF_SALES','PRODUCTION_COST'} else row['credit']-row['debit']
        earnings=totals['REVENUE']-totals['EXPENSE']-totals['COST_OF_SALES']-totals['PRODUCTION_COST']
        equity=totals['EQUITY']+earnings
        return {'assets':totals['ASSET'],'liabilities':totals['LIABILITY'],'equity':equity,
                'posted_equity':totals['EQUITY'],'current_earnings':earnings,
                'check':totals['ASSET']-totals['LIABILITY']-equity}

    @staticmethod
    def get_cash_flow(tenant_id,start_date,end_date):
        raise AccountingError('Cash-flow classification/reconciliation is not enabled; no synthetic zero adjustments are returned.')

    @staticmethod
    @financial_snapshot
    def get_profitability(tenant_id,start_date,end_date):
        """Company-wide net margin, never a package margin or operational GOP.

        Serialize with posting on the primary database. No replica lag, operational
        guesses, projections, account reclassification or write side effects.
        """
        from datetime import date
        from django.db import transaction
        from .validation import lock_company
        if type(start_date) is not date or type(end_date) is not date or start_date>end_date:
            raise AccountingError('A valid ordered economic-date interval is required.')
        with transaction.atomic():
            company=lock_company(tenant_id)
            from .models import JournalEntry
            if JournalEntry.plain_objects.filter(tenant_id=company.pk,is_posted=True,
                    date__gte=start_date,date__lte=end_date).exclude(base_currency=company.currency).exists():
                raise AccountingError('Historical base currencies require explicit reconciliation.')
            rows=ReportsEngine._totals(company.pk,end_date,start_date,database='default',
                account_types=('REVENUE','EXPENSE','COST_OF_SALES','PRODUCTION_COST'))
            income=expenses=ZERO
            sources=[]
            for row in rows:
                kind=row['account__type']
                if kind=='REVENUE':
                    amount=row['credit']-row['debit'];income+=amount
                elif kind in {'EXPENSE','COST_OF_SALES','PRODUCTION_COST'}:
                    amount=row['debit']-row['credit'];expenses+=amount
                else:continue
                sources.append({'account_id':str(row['account_id']),'code':row['account__code'],
                                'type':kind,'net_amount':format(amount,'.2f')})
            profit=income-expenses
            margin=(profit/income*100).quantize(Decimal('0.0001')) if income>ZERO else None
            return {'tenant_id':str(company.pk),'currency':company.currency,
                    'start_date':start_date.isoformat(),'end_date':end_date.isoformat(),
                    'posted_only':True,'valuation':'base_currency','source':'primary_ledger',
                    'scope':'company','revenue':format(income,'.2f'),'expenses':format(expenses,'.2f'),
                    'net_profit':format(profit,'.2f'),'sources':sources,
                    'net_margin':{'value':format(margin,'.4f') if margin is not None else None,
                                  'unit':'percent','formula':'(revenue-expenses)/revenue*100',
                                  'unavailable_reason':None if margin is not None else 'NON_POSITIVE_REVENUE'},
                    'related_reports':{'quick_ratio':'liquidez-acida (requires reviewed classification)'},
                    'pending_metrics':{
                        'revpar':'ROOM_REVENUE_MAPPING_AND_AVAILABLE_ROOM_NIGHTS_REQUIRED',
                        'goppar':'OPERATING_RESULT_MAPPING_AND_AVAILABLE_ROOM_NIGHTS_REQUIRED',
                        'package_margin':'VERIFIED_PACKAGE_COST_AND_REVENUE_ATTRIBUTION_REQUIRED'}}
