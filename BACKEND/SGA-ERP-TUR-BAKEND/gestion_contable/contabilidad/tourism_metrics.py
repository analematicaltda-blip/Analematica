"""Reviewed daily room capacity and timestamp-bounded hotel ratios.
No historical inventory guessed from today's rooms, no room price projections,
no bank/fiscal acceptance, and no package margin substituted by company margin.
"""
from datetime import date,datetime,timedelta
from decimal import Decimal,localcontext,ROUND_HALF_UP
import re
from uuid import UUID,uuid5
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from apps.turismo.models import TourismProvider
from apps.turismo.services.company_identity import resolve_company
from apps.core_erp.accounting.validation import lock_company,current_actor
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.models import Account,LedgerEntry
from apps.core_erp.accounting.opening_balances import inspect_opening
from apps.core_erp.outbox_models import OutboxEvent
from ...gestion_operativa.modulos_especializados.hoteles.models import Room

NS=UUID('bb7971fa-753d-4421-bc12-9a96a99b4d65')
REVIEW='accounting.hotel-capacity.reviewed.v1'
RECORDED='accounting.hotel-capacity.recorded.v1'
ROLES={'room_revenue':{'REVENUE'},'other_operating_revenue':{'REVENUE'},'operating_expenses':{'EXPENSE','COST_OF_SALES','PRODUCTION_COST'},'excluded_nonoperating':{'REVENUE','EXPENSE','COST_OF_SALES','PRODUCTION_COST'}}

def _context(actor,provider_id):
    user=current_actor(actor)
    if getattr(user,'is_agent',False):raise PermissionDenied('Se requiere un titular personal.')
    provider=TourismProvider.objects.using('default').select_for_update().filter(pk=UUID(str(provider_id)),owner_id=user.pk,is_active=True,status='ACTIVE').first()
    if provider is None:raise PermissionDenied('Empresa no autorizada.')
    company=resolve_company(user,provider.pk).tenant;company=lock_company(company.pk)
    user=current_actor(user);resolve_company(user,provider.pk)
    if company.currency!='COP' or getattr(user,'is_agent',False):raise AccountingError('Explicit active COP books required.')
    return user,provider,company

def _day(value):
    parsed=date.fromisoformat(value)
    if parsed.isoformat()!=value:raise AccountingError('Canonical date required.')
    return parsed

def _mapping(company,mapping,*,active):
    if not isinstance(mapping,dict) or set(mapping)!=set(ROLES):raise AccountingError('Explicit room/other operating revenue and operating expense classifications required.')
    result={};seen=set()
    for role,types in ROLES.items():
        requested=mapping[role]
        if not isinstance(requested,list) or len(requested)>10:raise AccountingError('Each classification permits at most10 accounts.')
        ids=[str(UUID(str(item))) for item in requested]
        if len(set(ids))!=len(ids) or seen.intersection(ids):raise AccountingError('Accounts cannot be counted twice.')
        seen.update(ids)
        query=Account.plain_objects.using('default').filter(tenant=company,chart_of_accounts__tenant=company,pk__in=ids,type__in=types)
        if active:query=query.filter(is_active=True)
        if query.count()!=len(ids):raise AccountingError('Selected account scope, type or activity is incompatible.')
        result[role]=sorted(ids)
    if not result['room_revenue'] or not result['operating_expenses']:raise AccountingError('Room revenue and operating expense selections are required.')
    return result

def _inventory(provider):
    if Room.objects.using('default').filter(provider_id=provider.pk).exclude(room_type__provider_id=provider.pk,room_type__product__provider_id=provider.pk).exists():raise AccountingError('Room/type/product company mismatch.')
    rooms=list(Room.objects.using('default').select_for_update(of=('self','room_type','room_type__product')).filter(provider_id=provider.pk,room_type__provider_id=provider.pk,room_type__product__provider_id=provider.pk).select_related('room_type','room_type__product').order_by('pk')[:51])
    if not rooms or len(rooms)>50:raise AccountingError('This daily review requires1–50 existing physical rooms; larger or missing inventories need separate onboarding.')
    result=[];display=[]
    for room in rooms:
        kind=room.room_type;product=kind.product
        if kind.provider_id!=provider.pk or product.provider_id!=provider.pk:raise AccountingError('Room/type/product company mismatch.')
        if room.housekeeping_status not in Room.HousekeepingStatus.values:raise AccountingError('Unknown room availability state.')
        eligible=room.is_active and kind.is_active and product.is_active and room.housekeeping_status=='CLEAN'
        result.append({'id':str(room.pk),'room_type_id':str(kind.pk),'product_id':str(product.pk),'room_active':room.is_active,'type_active':kind.is_active,'product_active':product.is_active,'housekeeping_status':room.housekeeping_status,'eligible':bool(eligible)})
        display.append({'id':str(room.pk),'label':room.numero_habitacion+' · '+product.nombre,'eligible':bool(eligible),'state':room.housekeeping_status})
    return result,display

def _snapshot(company,provider,day,room_ids,mapping):
    if _day(day)!=timezone.localdate():raise AccountingError('Only today may be observed; past/future capacity is never inferred from current inventory.')
    if not isinstance(room_ids,list) or len(room_ids)>50:raise AccountingError('Select an explicit bounded list, including an explicit empty selection for zero availability.')
    chosen=sorted(str(UUID(str(item))) for item in room_ids)
    if len(chosen)!=len(set(chosen)):raise AccountingError('Room repeated in daily capacity.')
    inventory,_=_inventory(provider)
    if set(chosen)-{row['id'] for row in inventory if row['eligible']}:raise AccountingError('Selected room unavailable or foreign.')
    return {'company_id':str(company.pk),'provider_id':str(provider.pk),'day':day,'room_ids':chosen,'inventory':inventory,'mapping':_mapping(company,mapping,active=True),'unit':'available_room_day','source':'owner_reviewed_current_physical_inventory','independently_verified':False}

def _records(company,provider,day=None):
    query=OutboxEvent.objects.using('default').filter(event_type=RECORDED,payload__company_id=str(company.pk),payload__provider_id=str(provider.pk))
    return query.filter(payload__day=day) if day else query

def _verified(row,company,provider):
    body=row.payload.get('observation');snap=body.get('snapshot') if isinstance(body,dict) else None
    if not isinstance(snap,dict) or fingerprint(body)!=row.payload.get('observation_digest') or snap.get('company_id')!=str(company.pk) or snap.get('provider_id')!=str(provider.pk) or row.payload.get('day')!=snap.get('day') or row.payload.get('revision')!=body.get('revision') or type(body.get('revision')) is not int or body['revision']<1:
        raise AccountingError('Daily capacity evidence changed.')
    review=OutboxEvent.objects.using('default').filter(pk=row.payload.get('review_id'),event_type=REVIEW,payload__company_id=str(company.pk),payload__provider_id=str(provider.pk)).first()
    if review is None or review.pk!=uuid5(NS,'review:'+fingerprint(body)) or review.payload.get('review')!=body or review.payload.get('review_digest')!=fingerprint(body):raise AccountingError('Daily capacity review origin missing or changed.')
    known=row.created_at.isoformat()
    if row.payload.get('known_at')!=known or row.payload.get('record_digest')!=fingerprint({'observation':body,'known_at':known}):raise AccountingError('Capacity knowledge timestamp changed.')
    if row.pk!=uuid5(NS,'recorded:'+str(company.pk)+':'+snap['day']+':'+str(body['revision'])):raise AccountingError('Capacity identity mismatch.')
    if len(snap.get('room_ids',[]))!=len(set(snap.get('room_ids',[]))):raise AccountingError('Duplicated capacity source.')
    return body

@transaction.atomic
def sources(*,actor,provider_id):
    user,provider,company=_context(actor,provider_id);inventory,rooms=_inventory(provider)
    accounts=list(Account.plain_objects.using('default').filter(tenant=company,chart_of_accounts__tenant=company,is_active=True,type__in={'REVENUE','EXPENSE','COST_OF_SALES','PRODUCTION_COST'}).order_by('code','pk')[:201])
    latest=_records(company,provider,timezone.localdate().isoformat()).order_by('-payload__revision').first()
    revision=_verified(latest,company,provider)['revision'] if latest else 0
    return {'company_id':str(company.pk),'provider_id':str(provider.pk),'day':timezone.localdate().isoformat(),'read_only':True,'rooms':rooms,'revision':revision,'accounts':[{'id':str(a.pk),'code':a.code,'name':a.name,'type':a.type} for a in accounts[:200]],'accounts_truncated':len(accounts)>200,'independently_verified':False}

@transaction.atomic
def review_capacity(*,actor,provider_id,day,room_ids,mapping,evidence_digest,expected_revision,confirmed):
    user,provider,company=_context(actor,provider_id)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0 or not isinstance(evidence_digest,str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest):raise AccountingError('First explicit review, revision and evidence digest required.')
    snapshot=_snapshot(company,provider,day,room_ids,mapping);old=_records(company,provider,day).order_by('-payload__revision').first();previous=_verified(old,company,provider)['revision'] if old else 0
    if expected_revision!=previous:raise AccountingError('Daily capacity revision changed; reload.')
    body={'snapshot':snapshot,'reviewed_by':str(user.pk),'evidence_digest':evidence_digest,'expected_revision':previous,'revision':previous+1}
    identifier=uuid5(NS,'review:'+fingerprint(body));payload={'company_id':str(company.pk),'provider_id':str(provider.pk),'review':body,'review_digest':fingerprint(body)}
    existing=OutboxEvent.objects.using('default').filter(pk=identifier).first()
    if existing and (existing.event_type!=REVIEW or existing.payload!=payload):raise AccountingError('Capacity review identity conflict.')
    if existing is None:OutboxEvent.objects.using('default').create(id=identifier,event_type=REVIEW,domain='accounting',aggregate_root=str(provider.pk),payload=payload,version=1)
    return {'company_id':str(company.pk),'review_id':str(identifier),'preview':body,'ledger_written':False,'independently_verified':False}

@transaction.atomic
def record_capacity(*,actor,provider_id,review_id,confirmed):
    user,provider,company=_context(actor,provider_id)
    if confirmed is not True:raise AccountingError('Second explicit daily-capacity confirmation required.')
    row=OutboxEvent.objects.using('default').filter(pk=UUID(str(review_id)),event_type=REVIEW,payload__company_id=str(company.pk),payload__provider_id=str(provider.pk)).first();body=row.payload.get('review') if row else None
    if not isinstance(body,dict) or fingerprint(body)!=row.payload.get('review_digest') or body.get('reviewed_by')!=str(user.pk):raise AccountingError('Capacity review/reviewer changed.')
    snap=body['snapshot'];identifier=uuid5(NS,'recorded:'+str(company.pk)+':'+snap['day']+':'+str(body['revision']))
    payload={'company_id':str(company.pk),'provider_id':str(provider.pk),'day':snap['day'],'revision':body['revision'],'observation':body,'observation_digest':fingerprint(body),'review_id':str(row.pk)}
    existing=OutboxEvent.objects.using('default').filter(pk=identifier).first()
    if existing:
        known=existing.created_at.isoformat();payload={**payload,'known_at':known,'record_digest':fingerprint({'observation':body,'known_at':known})}
        if existing.event_type!=RECORDED or existing.payload!=payload:raise AccountingError('Another capacity observation already used this version.')
        _verified(existing,company,provider)
        return {'company_id':str(company.pk),'observation_id':str(identifier),'revision':body['revision'],'replayed':True,'ledger_written':False,'independently_verified':False}
    current=_snapshot(company,provider,snap['day'],snap['room_ids'],snap['mapping'])
    if current!=snap:raise AccountingError('Room inventory or classification changed after review.')
    old=_records(company,provider,snap['day']).order_by('-payload__revision').first();previous=_verified(old,company,provider)['revision'] if old else 0
    if previous!=body['expected_revision']:raise AccountingError('Capacity revision changed before confirmation.')
    recorded=OutboxEvent.objects.using('default').create(id=identifier,event_type=RECORDED,domain='accounting',aggregate_root=str(provider.pk),payload=payload,version=1)
    if recorded.created_at<row.created_at or (old is not None and recorded.created_at<old.created_at):raise AccountingError('Knowledge clock moved backward; observation not recorded.')
    known=recorded.created_at.isoformat();sealed={**payload,'known_at':known,'record_digest':fingerprint({'observation':body,'known_at':known})}
    OutboxEvent.objects.using('default').filter(pk=recorded.pk).update(payload=sealed)
    recorded.payload=sealed;_verified(recorded,company,provider)
    return {'company_id':str(company.pk),'observation_id':str(identifier),'revision':body['revision'],'replayed':False,'ledger_written':False,'independently_verified':False}

def _number(cents):return ('-' if cents<0 else '')+f'{abs(cents)//100}.{abs(cents)%100:02d}'

def _financial(company,mapping,start,end,as_of):
    inspect_opening(company.pk,cutoff=end)
    rows=list(LedgerEntry.plain_objects.using('default').filter(tenant=company,journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__date__gte=start,journal_entry__date__lte=end,account__type__in=set().union(*ROLES.values())).filter(journal_entry__posted_at__lte=as_of).select_related('account','account__chart_of_accounts','journal_entry').order_by('journal_entry_id','pk')[:2001])
    # A missing publication timestamp is unknown, not a license to backfill it.
    if LedgerEntry.plain_objects.using('default').filter(tenant=company,journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__date__gte=start,journal_entry__date__lte=end,account__type__in=set().union(*ROLES.values()),journal_entry__posted_at__isnull=True,journal_entry__created_at__lte=as_of).exists():raise AccountingError('Missing posting timestamps require reconciliation.')
    if len(rows)>2000:raise AccountingError('Narrow the financial window: more than2000 relevant lines.')
    lookup={identifier:role for role,ids in mapping.items() for identifier in ids};totals={role:0 for role in ROLES};checked=set();unmapped=set();source=[]
    for row in rows:
        journal=row.journal_entry
        if journal.created_at>journal.posted_at or row.account.tenant_id!=company.pk or row.account.chart_of_accounts.tenant_id!=company.pk or journal.hash_version!='v2' or journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=1 or row.currency!='COP' or row.debit_amount<0 or row.credit_amount<0 or row.amount_transaction!=row.debit_amount+row.credit_amount or row.amount_base!=row.debit_amount+row.credit_amount or (row.debit_amount>0)==(row.credit_amount>0):raise AccountingError('Financial source scope or valuation requires reconciliation.')
        if journal.pk not in checked:
            if journal.compute_hash()!=journal.system_hash:raise AccountingError('Financial journal integrity mismatch.')
            checked.add(journal.pk)
        role=lookup.get(str(row.account_id))
        if role is None:unmapped.add(str(row.account_id));continue
        debit=int(format(row.debit_amount,'.2f').replace('.',''));credit=int(format(row.credit_amount,'.2f').replace('.',''))
        amount=credit-debit if role!='operating_expenses' else debit-credit;totals[role]+=amount
        source.append({'ledger_line_id':str(row.pk),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'account_id':str(row.account_id),'role':role,'amount':_number(amount),'posted_at':journal.posted_at.isoformat()})
    return totals,source,sorted(unmapped)

@transaction.atomic
def metrics(*,actor,provider_id,since,until,as_of=None):
    user,provider,company=_context(actor,provider_id);start=_day(since);end=_day(until);now=timezone.now()
    cutoff=datetime.fromisoformat(as_of.replace('Z','+00:00')) if isinstance(as_of,str) else now if as_of is None else None
    if cutoff is None or timezone.is_naive(cutoff) or cutoff>now or start>end or (end-start).days>30 or end>timezone.localdate(cutoff):raise AccountingError('Ordered window of at most31 days and nonfuture aware knowledge cutoff required.')
    found=list(_records(company,provider).filter(payload__day__gte=since,payload__day__lte=until,created_at__lte=cutoff).order_by('-payload__revision')[:501])
    if len(found)>500:raise AccountingError('Capacity history exceeds the bounded window.')
    by_day={}
    for row in found:
        day=row.payload.get('day')
        if day in by_day:continue
        body=_verified(row,company,provider)
        by_day[day]=(row,body)
    dates=[(start+timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
    missing=[day for day in dates if day not in by_day]
    result={'schema':'sgacd-hotel-metrics-v1','company_id':str(company.pk),'since':since,'until':until,'as_of':cutoff.isoformat(),'currency':'COP','read_only':True,'ledger_written':False,'revpar':None,'goppar':None,'room_revenue':None,'other_operating_revenue':None,'operating_expenses':None,'excluded_nonoperating':None,'operating_profit':None,'available_room_days':None,'missing_capacity_days':missing,'capacity_sources':[],'financial_sources':[],'unmapped_account_ids':[],'package_margin':None,'package_margin_reason':'PACKAGE_COST_ALLOCATION_REQUIRED','scope':'owner_reviewed_operating_accounts_and_daily_capacity','reconstruction':'recorded_knowledge_timestamps_not_certified_original_publication','independently_verified':False}
    if not by_day:return {**result,'unavailable_reason':'DAILY_CAPACITY_REQUIRED'}
    selected=[by_day[day] for day in sorted(by_day)];mapping=_mapping(company,selected[0][1]['snapshot']['mapping'],active=False)
    if any(body['snapshot']['mapping']!=mapping for row,body in selected):return {**result,'unavailable_reason':'CLASSIFICATION_CHANGED_WITHIN_WINDOW'}
    totals,financial,unmapped=_financial(company,mapping,start,end,cutoff)
    denominator=sum(len(body['snapshot']['room_ids']) for row,body in selected);profit=totals['room_revenue']+totals['other_operating_revenue']-totals['operating_expenses']
    result.update({role:_number(amount) for role,amount in totals.items()});result.update({'operating_profit':_number(profit),'available_room_days':denominator,'financial_sources':financial,'unmapped_account_ids':unmapped,'capacity_sources':[{'observation_id':str(row.pk),'day':body['snapshot']['day'],'revision':body['revision'],'available_rooms':len(body['snapshot']['room_ids']),'known_at':row.created_at.isoformat()} for row,body in selected]})
    if missing:return {**result,'unavailable_reason':'MISSING_DAILY_CAPACITY'}
    if unmapped:return {**result,'unavailable_reason':'UNCLASSIFIED_FINANCIAL_ACCOUNTS'}
    if denominator==0:return {**result,'unavailable_reason':'ZERO_AVAILABLE_ROOM_DAYS'}
    with localcontext() as ctx:
        ctx.prec=50
        result['revpar']=format((Decimal(totals['room_revenue'])/100/denominator).quantize(Decimal('.0001'),rounding=ROUND_HALF_UP),'.4f')
        result['goppar']=format((Decimal(profit)/100/denominator).quantize(Decimal('.0001'),rounding=ROUND_HALF_UP),'.4f')
    return {**result,'unavailable_reason':None}
