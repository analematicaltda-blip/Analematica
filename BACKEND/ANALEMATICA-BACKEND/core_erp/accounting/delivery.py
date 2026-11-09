"""Opt-in local outbox consumer. No network, funds transfer or external acknowledgment.
An expired lease may be reclaimed; the consumer receipt prevents duplicate effects.
"""
import os
import secrets
from datetime import timedelta
from decimal import Decimal
from django.db import transaction,connection,DatabaseError
from django.db.models import Q,Count,Sum
from django.utils import timezone
from .delivery_models import AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance
from .models import JournalEntry,Account
from .ledger_engine import LedgerEngine,rows
from .validation import lock_company
from .integrity import fingerprint
from .exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent

CONSUMER='accounting.daily-balance.v1'
EVENT='accounting.entry.posted.v2'
MAX_ATTEMPTS=5
LEASE_SECONDS=60

class ProjectionRejected(AccountingError):pass
class LeaseLost(AccountingError):pass
class ProjectorDisabled(AccountingError):pass


def enabled():
    if os.environ.get('ACCOUNTING_LOCAL_PROJECTION_ENABLED')!='1':
        raise ProjectorDisabled('Local accounting projection is disabled.')


def bounded_limit(value):
    if isinstance(value,bool) or not isinstance(value,int) or not 1<=value<=100:
        raise AccountingError('Batch size must be from 1 to 100.')
    return value


def envelope_digest(event):
    if (event.event_type!=EVENT or event.domain!='accounting' or event.version!=2
            or event.aggregate_root!=str(event.pk) or not isinstance(event.payload,dict)):
        raise ProjectionRejected('Unsupported accounting envelope.')
    try:
        return fingerprint({'event_id':str(event.pk),'type':event.event_type,'domain':event.domain,
                            'version':event.version,'aggregate':event.aggregate_root,'payload':event.payload})
    except AccountingError:raise ProjectionRejected('Invalid accounting envelope.') from None


@transaction.atomic
def enqueue(tenant_id,limit=50):
    enabled();limit=bounded_limit(limit);lock_company(tenant_id)
    events=list(OutboxEvent.objects.select_for_update().filter(event_type=EVENT,payload__tenant_id=str(tenant_id))
                .exclude(accounting_deliveries__consumer=CONSUMER).order_by('created_at','pk')[:limit])
    quarantined=0
    for event in events:
        state='PENDING';error='';digest=''
        try:digest=envelope_digest(event)
        except ProjectionRejected:state='QUARANTINED';error='INVALID_ENVELOPE';quarantined+=1
        AccountingDelivery.objects.create(tenant_id=tenant_id,event=event,consumer=CONSUMER,
            status=state,payload_digest=digest,last_error_code=error)
    return {'enqueued':len(events),'quarantined':quarantined}


@transaction.atomic
def claim(tenant_id):
    enabled()
    from apps.core_erp.tenancy.models import Tenant
    if not Tenant.objects.filter(pk=tenant_id,is_active=True,state='ACTIVE').exists():
        raise AccountingError('Active accounting company required.')
    now=timezone.now()
    base=AccountingDelivery.objects.filter(tenant_id=tenant_id,consumer=CONSUMER)
    base.filter(status='LEASED',lease_until__lte=now,attempts__gte=MAX_ATTEMPTS).update(
        status='QUARANTINED',lease_token=None,lease_until=None,last_error_code='LEASE_RETRIES_EXHAUSTED',updated_at=now)
    eligible=Q(status__in=['PENDING','RETRY'],next_attempt_at__lte=now)|Q(status='LEASED',lease_until__lte=now)
    query=base.filter(eligible,attempts__lt=MAX_ATTEMPTS).order_by('created_at','pk')
    if connection.features.has_select_for_update_skip_locked:query=query.select_for_update(skip_locked=True)
    else:query=query.select_for_update()
    row=query.first()
    if row is None:return None
    token=secrets.token_hex(24)
    changed=base.filter(pk=row.pk,status=row.status,attempts=row.attempts,lease_token=row.lease_token).update(
        status='LEASED',attempts=row.attempts+1,lease_token=token,lease_until=now+timedelta(seconds=LEASE_SECONDS),last_error_code='',updated_at=now)
    if changed!=1:return None
    return {'id':row.pk,'token':token}


def valid_lease(row,token,now):
    if not isinstance(token,str) or len(token)!=48 or not token.isascii():return False
    return (row.status=='LEASED' and row.lease_token and secrets.compare_digest(row.lease_token,token)
            and row.lease_until is not None and row.lease_until>now)


@transaction.atomic
def consume(tenant_id,delivery_id,token):
    enabled();lock_company(tenant_id)
    row=AccountingDelivery.objects.select_for_update().get(pk=delivery_id,tenant_id=tenant_id,consumer=CONSUMER)
    if not valid_lease(row,token,timezone.now()):raise LeaseLost('Delivery lease is no longer valid.')
    event=OutboxEvent.objects.select_for_update().get(pk=row.event_id)
    if envelope_digest(event)!=row.payload_digest:raise ProjectionRejected('Envelope changed after enqueue.')
    journal=JournalEntry.plain_objects.select_for_update().filter(pk=event.pk,tenant_id=tenant_id,is_posted=True,hash_version='v2').first()
    if journal is None:raise ProjectionRejected('Posted v2 journal unavailable in this company.')
    lines=rows(journal,lock=True)
    if LedgerEngine.calculate_hash(journal)!=journal.system_hash:raise ProjectionRejected('Journal integrity rejected.')
    try:LedgerEngine.validate_balance(journal,lines)
    except AccountingError:raise ProjectionRejected('Journal balance rejected.') from None
    expected={'tenant_id':str(journal.tenant_id),'entry_id':str(journal.pk),'actor_id':journal.created_by_id,
              'total_debit':format(sum((line.debit_amount for line in lines),Decimal('0.00')),'.2f'),
              'currency':journal.currency,'base_currency':journal.base_currency,'system_hash':journal.system_hash,'hash_version':'v2'}
    if event.payload!=expected:raise ProjectionRejected('Event does not match its accounting journal.')
    prior=AccountingProjectionReceipt.objects.filter(event=event,consumer=CONSUMER).first()
    applied=False
    if prior:
        if (prior.payload_digest!=row.payload_digest or prior.journal_hash!=journal.system_hash
                or prior.journal_id!=journal.pk or prior.tenant_id!=journal.tenant_id):
            raise ProjectionRejected('Consumer receipt mismatch.')
    else:
        for line in lines:
            amount=line.amount_base
            if amount<=0:raise ProjectionRejected('Base valuation unavailable.')
            balance,_=AccountingDailyBalance.objects.get_or_create(tenant_id=tenant_id,account_id=line.account_id,
                economic_date=journal.date,currency=journal.base_currency)
            if line.debit_amount:balance.debit+=amount
            else:balance.credit+=amount
            balance.save(update_fields=['debit','credit','updated_at'])
        AccountingProjectionReceipt.objects.create(tenant_id=tenant_id,event=event,journal=journal,consumer=CONSUMER,
            payload_digest=row.payload_digest,journal_hash=journal.system_hash)
        applied=True
    if not valid_lease(row,token,timezone.now()):raise LeaseLost('Lease expired before committing projection.')
    row.status='DELIVERED';row.delivered_at=timezone.now();row.lease_token=None;row.lease_until=None;row.last_error_code=''
    row.save(update_fields=['status','delivered_at','lease_token','lease_until','last_error_code','updated_at'])
    # Outbox status and published_at remain unchanged: no Kafka publication happened.
    return {'applied':applied,'duplicate_effect':False,'external_publication_verified':False}


@transaction.atomic
def failed(tenant_id,delivery_id,token,*,permanent=False,code='TRANSIENT_FAILURE'):
    row=AccountingDelivery.objects.select_for_update().get(pk=delivery_id,tenant_id=tenant_id,consumer=CONSUMER)
    if not isinstance(token,str) or not token.isascii() or row.status!='LEASED' or not row.lease_token or not secrets.compare_digest(row.lease_token,token):return False
    row.status='QUARANTINED' if permanent or row.attempts>=MAX_ATTEMPTS else 'RETRY'
    row.last_error_code=code if code in {'TRANSIENT_FAILURE','INTEGRITY_REJECTED','PROJECTOR_DISABLED','UNEXPECTED_FAILURE'} else 'UNEXPECTED_FAILURE'
    row.next_attempt_at=timezone.now()+timedelta(seconds=min(2**min(row.attempts,8),300))
    row.lease_token=None;row.lease_until=None
    row.save(update_fields=['status','last_error_code','next_attempt_at','lease_token','lease_until','updated_at'])
    return row.status


def run_batch(tenant_id,limit=50):
    enabled();limit=bounded_limit(limit);added=enqueue(tenant_id,limit)
    result={'enqueued':added['enqueued'],'delivered':0,'quarantined':added['quarantined'],'retry':0,'lease_lost':0,'local_only':True}
    for _ in range(limit):
        lease=claim(tenant_id)
        if lease is None:break
        try:consume(tenant_id,lease['id'],lease['token']);result['delivered']+=1
        except LeaseLost:result['lease_lost']+=1
        except ProjectionRejected:
            state=failed(tenant_id,lease['id'],lease['token'],permanent=True,code='INTEGRITY_REJECTED')
            result['quarantined' if state else 'lease_lost']+=1
        except ProjectorDisabled:
            failed(tenant_id,lease['id'],lease['token'],code='PROJECTOR_DISABLED');raise
        except (DatabaseError,TimeoutError,OSError):
            state=failed(tenant_id,lease['id'],lease['token'],code='TRANSIENT_FAILURE')
            result['quarantined' if state=='QUARANTINED' else 'retry' if state else 'lease_lost']+=1
        except Exception:
            state=failed(tenant_id,lease['id'],lease['token'],permanent=True,code='UNEXPECTED_FAILURE')
            result['quarantined' if state else 'lease_lost']+=1
    return result


@transaction.atomic
def status(tenant_id):
    lock_company(tenant_id)
    states={row['status']:row['count'] for row in AccountingDelivery.objects.filter(tenant_id=tenant_id,consumer=CONSUMER).values('status').annotate(count=Count('pk'))}
    journals=JournalEntry.plain_objects.filter(tenant_id=tenant_id,is_posted=True)
    count=journals.count();receipts=AccountingProjectionReceipt.objects.filter(tenant_id=tenant_id,consumer=CONSUMER).count()
    legacy=journals.exclude(hash_version='v2').exists()
    opening=Account.plain_objects.filter(tenant_id=tenant_id).exclude(initial_balance=0).exists()
    complete=count==receipts and not legacy and not opening and not any(value for key,value in states.items() if key!='DELIVERED')
    failures=[{'event_id':str(row.event_id),'status':row.status,'attempts':row.attempts,
               'next_attempt_at':row.next_attempt_at.isoformat(),'error_code':row.last_error_code}
              for row in AccountingDelivery.objects.filter(tenant_id=tenant_id,consumer=CONSUMER,status__in=['RETRY','QUARANTINED']).order_by('-updated_at','pk')[:20]]
    values=[]
    if complete:
        values=[{'account_id':str(row['account_id']),'currency':row['currency'],'debit':format(row['debit'],'.2f'),'credit':format(row['credit'],'.2f')}
                for row in AccountingDailyBalance.objects.filter(tenant_id=tenant_id).values('account_id','currency').annotate(debit=Sum('debit'),credit=Sum('credit')).order_by('account_id','currency')]
    return {'consumer':CONSUMER,'enabled':os.environ.get('ACCOUNTING_LOCAL_PROJECTION_ENABLED')=='1',
            'states':states,'failures':failures,'failures_truncated':sum(states.get(key,0) for key in ['RETRY','QUARANTINED'])>len(failures),
            'source_journals':count,'journal_receipt_gap':count-receipts,'receipts':receipts,'complete':complete,
            'legacy_reconciliation_required':legacy,'opening_reconciliation_required':opening,'balances':values,
            'external_publication_verified':False,'valuation':'base_currency','authoritative_report':'balance-prueba'}
