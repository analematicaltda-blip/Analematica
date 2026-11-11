"""Shared ACID ledger: explicit scope, tenant serialization and transactional outbox.
This service records accounting facts; it never sends payments or publishes to Kafka.
"""
import hashlib
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone
from .models import JournalEntry, LedgerEntry, Account, FiscalPeriod, AccountingEventReceipt, AccountingAuditLog
from .exceptions import AccountingError, FiscalPeriodClosedError, TenantMismatchError, DuplicateReversalError, InactiveAccountError
from .validation import validate_lines, lock_company, current_actor, money
from .integrity import journal_hash, fingerprint
from .journal_service import JournalService
from .posting_rules import PostingRules

GENESIS='GENESIS_SARITA_2026'


def scope(tenant_id):
    if tenant_id is None:
        from apps.core_erp.tenancy.utils import get_current_tenant_id
        tenant_id=get_current_tenant_id()
    if not tenant_id:raise TenantMismatchError('An explicit or authenticated-context accounting company is required.')
    return tenant_id


def rows(entry,lock=False):
    query=LedgerEntry.plain_objects.filter(journal_entry_id=entry.pk).select_related('account').order_by('pk')
    if lock:query=query.select_for_update(of=('self',))
    return list(query)


def historical_reversal_valuation(entry,lines):
    """Neutral reversal only: exact original accounts/sides and recorded base values."""
    from collections import defaultdict
    original=JournalEntry.plain_objects.select_for_update().filter(pk=entry.reversed_entry_id,tenant_id=entry.tenant_id,is_posted=True).first()
    if original is None or original.is_reversal or original.hash_version!='v2':
        raise AccountingError('A verified v2 original is required for a foreign-currency neutral reversal.')
    if original.currency!=entry.currency or original.base_currency!=entry.base_currency:
        raise AccountingError('Reversal currencies must match the original.')
    if JournalEntry.plain_objects.filter(tenant_id=entry.tenant_id,reversed_entry_id=original.pk,is_posted=True).exclude(pk=entry.pk).exists():
        raise DuplicateReversalError('The original already has a posted reversal.')
    originals=rows(original,lock=True)
    if original.system_hash!=LedgerEngine.calculate_hash(original):raise AccountingError('Original journal integrity mismatch.')
    LedgerEngine.validate_balance(original,originals)
    rate=original.exchange_rate
    if not rate.is_finite() or rate<=0:raise AccountingError('Invalid historical reversal rate.')
    expected=defaultdict(list)
    for row in originals:
        amount=row.debit_amount or row.credit_amount
        if row.amount_transaction!=amount or row.amount_base!=money((amount*rate).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)):
            raise AccountingError('Historical valuation requires reconciliation.')
        expected[(row.account_id,row.credit_amount,row.debit_amount,row.currency)].append(row.amount_base)
    values={}
    for line in lines:
        key=(line.account_id,line.debit_amount,line.credit_amount,line.currency)
        if not expected[key]:raise AccountingError('A neutral reversal must exactly invert every original line.')
        values[line.pk]=expected[key].pop()
    if any(expected.values()):raise AccountingError('A neutral reversal cannot omit original lines.')
    return rate,values


class LedgerEngine:
    @staticmethod
    def calculate_hash(entry, previous_hash=None):
        previous=previous_hash if previous_hash is not None else (entry.previous_hash or GENESIS)
        if entry.hash_version=='v2':return journal_hash(entry,rows(entry),previous)
        # Preserve the legacy engine algorithm for verification only, never rehash old rows.
        total=sum((line.debit_amount for line in rows(entry)),Decimal('0.00'))
        payload=f"{entry.id}{entry.date}{entry.reference or ''}{total}{previous}"
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def validate_balance(entry,lines=None):
        lines=rows(entry) if lines is None else lines
        if not entry.tenant_id:raise TenantMismatchError('An accounting company is required.')
        for line in lines:
            if str(line.tenant_id)!=str(entry.tenant_id) or str(line.account.tenant_id)!=str(entry.tenant_id):
                raise TenantMismatchError('A line or account belongs to another company.')
        validate_lines([{'debit':line.debit_amount,'credit':line.credit_amount} for line in lines])
        return True

    @staticmethod
    @transaction.atomic
    def post_event(event_type,payload,*,actor=None):
        if not isinstance(payload,dict):raise AccountingError('An event payload is required.')
        if not isinstance(event_type,str) or not 1<=len(event_type)<=100:raise AccountingError('Invalid event type.')
        tenant_id=scope(payload.get('tenant_id') or payload.get('organization_id'))
        lock_company(tenant_id);user=current_actor(actor)
        event_id=payload.get('financial_event_id') or payload.get('reference')
        if not isinstance(event_id,str) or not 1<=len(event_id)<=255:
            raise AccountingError('A stable financial_event_id is required.')
        digest=fingerprint({'event_type':event_type,'payload':payload,'actor_id':user.pk})
        receipt=AccountingEventReceipt.objects.select_related('journal').filter(tenant_id=tenant_id,event_id=event_id).first()
        if receipt:
            if receipt.payload_hash!=digest or receipt.journal.financial_event_id!=event_id or str(receipt.journal.tenant_id)!=str(tenant_id):raise AccountingError('Event id reused with a different contract.')
            return LedgerEngine.post_entry(receipt.journal_id,tenant_id=tenant_id,actor=user)
        if JournalEntry.plain_objects.filter(tenant_id=tenant_id,financial_event_id=event_id).exists():
            raise AccountingError('Legacy event requires reconciliation before replay.')
        rule=PostingRules.get_rule_for_event(event_type,payload)
        if not rule:raise AccountingError('No reviewed accounting rule for this event.')
        lines=[]
        for line in rule:
            left=money(line.get('debit',line.get('debit_amount',0)))
            right=money(line.get('credit',line.get('credit_amount',0)))
            if left or right:lines.append({**line,'debit':left,'credit':right})
        entry_date=payload.get('entry_date')
        if entry_date is None:entry_date=timezone.localdate()
        else:
            try:entry_date=date.fromisoformat(entry_date)
            except (TypeError,ValueError):raise AccountingError('Invalid economic date.') from None
        entry=JournalService.create_entry(str(tenant_id),entry_date,'Accounting event: '+event_type,lines,
            reference=str(payload.get('reference','')),created_by=user,
            currency=payload.get('currency','COP'),base_currency=payload.get('base_currency','COP'))
        entry.event_type=event_type;entry.financial_event_id=event_id;entry.rule_version=PostingRules.VERSION
        entry.correlation_id=payload.get('_correlation_id');entry.save()
        entry=LedgerEngine.post_entry(entry.pk,tenant_id=tenant_id,actor=user)
        AccountingEventReceipt.objects.create(tenant_id=tenant_id,event_id=event_id,payload_hash=digest,journal=entry)
        return entry

    @staticmethod
    @transaction.atomic
    def post_lines(*,tenant_id,entry_date,description,lines_data,actor,idempotency_key,period_id=None):
        lock_company(tenant_id);user=current_actor(actor)
        if not isinstance(idempotency_key,str) or not 1<=len(idempotency_key)<=255:
            raise AccountingError('A stable idempotency key is required for manual creation/posting.')
        if idempotency_key.startswith('fx-settlement:'):
            from .fx_settlement import authorize
            authorize(tenant_id,user.pk,idempotency_key)
        if idempotency_key.startswith('opening-chunks:'):
            from .chunked_opening import authorize
            authorize(tenant_id,user.pk,idempotency_key)
        normalized=validate_lines(lines_data)
        contract={'schema':'manual-journal-v2','tenant_id':str(tenant_id),'actor_id':user.pk,
                  'date':entry_date.isoformat(),'description':description,'period_id':str(period_id) if period_id else None,
                  'lines':[{**row,'account':str(getattr(row.get('account'),'pk',row.get('account')))} for row in normalized]}
        digest=fingerprint(contract)
        existing=AccountingEventReceipt.objects.filter(tenant_id=tenant_id,event_id=idempotency_key).first()
        if existing:
            if existing.payload_hash!=digest or existing.journal.financial_event_id!=idempotency_key or str(existing.journal.tenant_id)!=str(tenant_id):raise AccountingError('Idempotency key reused with changed manual journal.')
            return LedgerEngine.post_entry(existing.journal_id,tenant_id=tenant_id,actor=user)
        if JournalEntry.plain_objects.filter(tenant_id=tenant_id,financial_event_id=idempotency_key).exists():
            raise AccountingError('Legacy financial event requires reconciliation.')
        entry=JournalService.create_entry(str(tenant_id),entry_date,description,normalized,
            created_by=user,period_id=period_id)
        entry.event_type='MANUAL';entry.financial_event_id=idempotency_key;entry.save()
        entry=LedgerEngine.post_entry(entry.pk,tenant_id=tenant_id,actor=user)
        AccountingEventReceipt.objects.create(tenant_id=tenant_id,event_id=idempotency_key,payload_hash=digest,journal=entry)
        return entry

    @staticmethod
    @transaction.atomic
    def post_entry(entry_id,*,tenant_id=None,actor=None,fx_review_id=None):
        tenant_id=scope(tenant_id);company=lock_company(tenant_id);user=current_actor(actor)
        identifier=getattr(entry_id,'pk',entry_id)
        hint=JournalEntry.plain_objects.get(pk=identifier,tenant_id=tenant_id)
        period=FiscalPeriod.plain_objects.select_for_update().get(pk=hint.period_id)
        entry=JournalEntry.plain_objects.select_for_update().get(pk=identifier,tenant_id=tenant_id)
        from . import reviewed_fx
        fx_reserved=bool(entry.financial_event_id and entry.financial_event_id.startswith('reviewed-fx-pending:'))
        fx_review=reviewed_fx.latest(company,str(entry.pk)) if entry.currency!=entry.base_currency or fx_reserved else None
        if not entry.is_posted and (fx_reserved or fx_review is not None) and fx_review_id is None:
            raise AccountingError('Pending reviewed FX draft requires its explicit second confirmation.')
        if fx_review_id is not None and (entry.currency==entry.base_currency or entry.is_reversal):
            raise AccountingError('Reviewed FX is only for initial foreign-currency posting.')
        if not entry.is_posted and entry.financial_event_id and entry.financial_event_id.startswith('fx-settlement:'):
            from .fx_settlement import authorize
            authorize(company.pk,user.pk,entry.financial_event_id)
        if not entry.is_posted and entry.financial_event_id and entry.financial_event_id.startswith('opening-chunks:'):
            from .chunked_opening import authorize
            authorize(company.pk,user.pk,entry.financial_event_id)
        if entry.is_posted:
            if entry.financial_event_id and entry.financial_event_id.startswith('opening-chunks:'):
                from .chunked_opening import verify_posted_origin
                verify_posted_origin(company,entry)
            if entry.financial_event_id and entry.financial_event_id.startswith('fx-settlement:'):
                from .fx_settlement import proof as verify_fx_settlement_origin
                verify_fx_settlement_origin(company,entry)
            if entry.financial_event_id and entry.financial_event_id.startswith('fx-revaluation:'):
                from .fx_revaluation import proof as verify_fx_balance_origin
                verify_fx_balance_origin(company,entry)
            if entry.financial_event_id and entry.financial_event_id.startswith('reviewed-fx:'):
                reviewed_fx.verify_posted_origin(company,user,entry)
            if entry.hash_version=='v2' and entry.system_hash!=LedgerEngine.calculate_hash(entry):
                raise AccountingError('Posted journal failed integrity verification.')
            return entry
        if entry.created_by_id is None or entry.created_by_id!=user.pk:
            raise AccountingError('The draft must identify the active responsible posting actor.')
        if period.tenant_id!=entry.tenant_id or period.status!='open' or not period.period_start or not period.period_end or not period.period_start<=entry.date<=period.period_end:
            raise FiscalPeriodClosedError('The fiscal period is closed or does not cover this company/date.')
        if entry.date>timezone.localdate():raise AccountingError('Future-dated journals remain drafts until their economic date.')
        if entry.base_currency!=company.currency:raise AccountingError('Base currency differs from company currency.')
        lines=rows(entry,lock=True);LedgerEngine.validate_balance(entry,lines)
        accounts={row.pk:row for row in Account.plain_objects.select_for_update(of=('self',)).select_related('chart_of_accounts').filter(
            pk__in=[line.account_id for line in lines]).order_by('pk')}
        for line in lines:
            account=accounts[line.account_id]
            if not account.is_active:raise InactiveAccountError('An account is inactive.')
            if account.tenant_id!=entry.tenant_id or account.chart_of_accounts.tenant_id!=entry.tenant_id:raise TenantMismatchError('Account/chart company changed.')
            line.account=account
            if line.currency!=entry.currency:raise AccountingError('Mixed transaction currencies require separate journals.')
        from ..fx.fx_engine import FXEngine
        rate=Decimal('1.000000');historical_values=None
        if entry.currency!=entry.base_currency and entry.is_reversal:
            rate,historical_values=historical_reversal_valuation(entry,lines)
            if entry.exchange_rate!=rate:raise AccountingError('Reversal must retain the recorded original rate.')
        elif entry.currency!=entry.base_currency and fx_review_id is not None:
            rate=reviewed_fx.rate_for_post(company,user,entry,fx_review_id)
        elif entry.currency!=entry.base_currency:
            moment=timezone.make_aware(datetime.combine(entry.date,time.max))
            try:rate=FXEngine.get_rate(entry.currency,entry.base_currency,as_of=min(timezone.now(),moment))
            except ValueError:raise AccountingError('A valid recorded FX rate is required; no fallback to 1.0.') from None
            if entry.exchange_rate!=Decimal('1') and entry.exchange_rate!=rate:
                raise AccountingError('Draft rate differs from the applicable recorded rate.')
        elif entry.exchange_rate!=Decimal('1'):
            raise AccountingError('Same-currency entries require a unit rate.')
        if not rate.is_finite() or rate<=0:raise AccountingError('Invalid FX rate.')
        entry.exchange_rate=rate
        debit_base=credit_base=Decimal('0.00')
        for line in lines:
            amount=line.debit_amount or line.credit_amount
            if line.amount_transaction and line.amount_transaction!=amount:
                raise AccountingError('Transaction amount differs from debit/credit.')
            line.amount_transaction=amount
            line.amount_base=historical_values[line.pk] if historical_values is not None else money((amount*rate).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))
            if line.debit_amount:debit_base+=line.amount_base
            else:credit_base+=line.amount_base
        if debit_base!=credit_base:raise AccountingError('Base-currency rounding requires an explicit reviewed adjustment.')
        LedgerEntry.plain_objects.bulk_update(lines,['amount_transaction','amount_base'])
        last=JournalEntry.plain_objects.filter(tenant_id=tenant_id,is_posted=True).order_by('-posted_at','-pk').first()
        if last and (not last.posted_at or not last.system_hash):raise AccountingError('Legacy chain requires reconciliation.')
        entry.previous_hash=last.system_hash if last else GENESIS
        entry.posted_at=max(timezone.now(),last.posted_at+timedelta(microseconds=1)) if last else timezone.now()
        entry.hash_version='v2';entry.system_hash=journal_hash(entry,lines,entry.previous_hash)
        entry.immutable_signature=None # A digest is not a digital signature.
        entry.is_posted=True;entry._validated_post=True;entry.save()
        AccountingAuditLog.objects.create(tenant_id=tenant_id,user=user,action='POST',reference_entry=entry,
            integrity_hash=fingerprint({'schema':'accounting-audit-v2','entry_id':str(entry.pk),'actor_id':user.pk,'action':'POST','journal_hash':entry.system_hash}))
        from apps.core_erp.outbox_models import OutboxEvent
        OutboxEvent.objects.create(id=entry.pk,event_type='accounting.entry.posted.v2',domain='accounting',
            aggregate_root=str(entry.pk),version=2,payload={'tenant_id':str(entry.tenant_id),'entry_id':str(entry.pk),
                'actor_id':user.pk,'total_debit':format(sum((l.debit_amount for l in lines),Decimal('0.00')),'.2f'),
                'currency':entry.currency,'base_currency':entry.base_currency,'system_hash':entry.system_hash,'hash_version':'v2'},status='PENDING')
        return entry

    @staticmethod
    @transaction.atomic
    def reverse_entry(journal_entry_id,reason='Reviewed reversal',*,tenant_id=None,actor=None):
        tenant_id=scope(tenant_id);company=lock_company(tenant_id);user=current_actor(actor)
        original=JournalEntry.plain_objects.select_for_update().get(pk=journal_entry_id,tenant_id=tenant_id)
        if original.financial_event_id and original.financial_event_id.startswith('fx-revaluation:'):
            from .fx_revaluation import proof as verify_fx_balance_origin
            verify_fx_balance_origin(company,original)
        if original.financial_event_id and original.financial_event_id.startswith('reviewed-fx:'):
            from .reviewed_fx import verify_posted_origin
            verify_posted_origin(company,user,original)
        if original.financial_event_id and original.financial_event_id.startswith('fx-settlement:'):
            from .fx_settlement import proof as verify_fx_settlement_origin
            verify_fx_settlement_origin(company,original)
        from .fx_settlement import protect_cash_reversal
        protect_cash_reversal(company,original)
        if original.financial_event_id and original.financial_event_id.startswith('opening-chunks:'):
            from .chunked_opening import verify_posted_origin
            verify_posted_origin(company,original)
        if not original.is_posted:raise AccountingError('Only posted journals can be reversed.')
        if original.is_reversal or JournalEntry.plain_objects.filter(tenant_id=tenant_id,reversed_entry_id=original.pk).exists():
            raise DuplicateReversalError('Journal already reversed or itself a reversal.')
        if original.hash_version=='v2' and original.system_hash!=LedgerEngine.calculate_hash(original):
            raise AccountingError('Original journal failed integrity verification.')
        from .native_return_reversal import require as require_reviewed_return_reconciliation
        require_reviewed_return_reconciliation(company,original,user.pk)
        # A receipt applied by any UI must first release its active recognition.
        # This runs under the same company lock as allocation and all postings.
        from apps.core_erp.outbox_models import OutboxEvent
        claims=OutboxEvent.objects.filter(event_type='accounting.reservation.advance-applied.v1',payload__company_id=str(original.tenant_id),payload__allocation__journal_id=str(original.pk))
        for claim in claims.iterator():
            recognition_id=claim.payload.get('recognition_journal_id')
            recognition=JournalEntry.plain_objects.filter(pk=recognition_id,tenant_id=tenant_id,is_posted=True,is_reversal=False).first() if recognition_id else None
            if recognition is None or recognition.compute_hash()!=recognition.system_hash:
                raise AccountingError('Advance application evidence requires reconciliation.')
            if not JournalEntry.plain_objects.filter(tenant_id=tenant_id,reversed_entry_id=recognition.pk,is_posted=True).exists():
                raise AccountingError('Reverse the active recognition before reversing its applied receipt.')
        lines=[{'account':row.account,'debit':row.credit_amount,'credit':row.debit_amount,
                'currency':row.currency,'amount_transaction':row.amount_transaction,'description':'Reviewed reversal'} for row in rows(original)]
        reversal=JournalService.create_entry(str(tenant_id),timezone.localdate(),str(reason)[:255],lines,
            reference=('REV-'+str(original.pk)),created_by=user,currency=original.currency,base_currency=original.base_currency,exchange_rate=original.exchange_rate)
        reversal.event_type='REVERSAL';reversal.is_reversal=True;reversal.reversed_entry_id=original.pk
        # Current period is checked independently; foreign values are validated against the original at posting.
        reversal.save();reversal=LedgerEngine.post_entry(reversal.pk,tenant_id=tenant_id,actor=user)
        AccountingAuditLog.objects.create(tenant_id=tenant_id,user=user,action='REVERSE',reference_entry=reversal,
            integrity_hash=fingerprint({'entry_id':str(reversal.pk),'original_id':str(original.pk),'actor_id':user.pk}))
        return reversal

    @staticmethod
    def validate_ledger_integrity(tenant_id):
        tenant_id=scope(tenant_id)
        entries=list(JournalEntry.plain_objects.filter(tenant_id=tenant_id,is_posted=True).order_by('posted_at','pk'))
        previous=GENESIS;errors=[]
        for index,entry in enumerate(entries):
            if index==0 and entry.hash_version=='legacy' and entry.previous_hash=='GENESIS_BLOCK_SARITA_V1':previous=entry.previous_hash
            if entry.previous_hash!=previous:errors.append('Broken chain: '+str(entry.pk))
            if entry.hash_version not in {'legacy','v2'}:errors.append('Unknown hash version: '+str(entry.pk))
            else:
                calculated=LedgerEngine.calculate_hash(entry,entry.previous_hash)
                if entry.system_hash!=calculated:
                    # Legacy model algorithm is also preserved for historic rows.
                    if entry.hash_version!='legacy' or entry.system_hash!=entry.compute_hash():errors.append('Invalid hash: '+str(entry.pk))
            try:LedgerEngine.validate_balance(entry)
            except AccountingError:errors.append('Invalid journal: '+str(entry.pk))
            previous=entry.system_hash
        return {'is_valid':not errors,'errors':errors,'entries_count':len(entries),'cryptographic_signature_verified':False}

    @staticmethod
    def get_trial_balance(tenant_id,cutoff_date=None):
        from .reports_engine import ReportsEngine
        return ReportsEngine.get_trial_balance(tenant_id,cutoff_date or timezone.localdate())
