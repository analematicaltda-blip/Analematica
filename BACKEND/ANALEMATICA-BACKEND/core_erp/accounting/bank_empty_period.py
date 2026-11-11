"""Two-step evidence for owner-declared zero-activity bank periods.
No synthetic statement rows, bank authentication, ledger posting or money movement.
"""
from datetime import datetime,timedelta
from uuid import UUID,uuid5
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from . import bank_reconciliation as bank
from .bank_period import assess
from .exceptions import AccountingError
from .integrity import fingerprint
from apps.core_erp.outbox_models import OutboxEvent

NS=UUID('30c31c41-a157-426d-9b56-4f289a828025')
REVIEW='accounting.empty-bank-period.reviewed.v1'
CONFIRMED='accounting.empty-bank-period.confirmed.v1'


def checked(company,row,kind):
    if row is None or row.event_type!=kind or row.domain!='accounting' or row.version!=1 or row.aggregate_root!=str(company.pk):raise AccountingError('Scoped empty-period evidence required.')
    body=row.payload.get('body')
    if not isinstance(body,dict) or body.get('company_id')!=str(company.pk) or row.payload!={'body':body,'digest':fingerprint(body)} or row.pk!=uuid5(NS,kind+':'+str(company.pk)+':'+body['request_id']):raise AccountingError('Empty-period evidence changed.')
    return body


def store(company,kind,body):
    return OutboxEvent.objects.create(id=uuid5(NS,kind+':'+str(company.pk)+':'+body['request_id']),event_type=kind,domain='accounting',aggregate_root=str(company.pk),version=1,payload={'body':body,'digest':fingerprint(body)})


def result(company,row):
    body=checked(company,row,REVIEW)
    applied=OutboxEvent.objects.filter(pk=uuid5(NS,CONFIRMED+':'+str(company.pk)+':'+body['request_id'])).first()
    if applied:
        proof=checked(company,applied,CONFIRMED)
        if proof!={'company_id':str(company.pk),'request_id':body['request_id'],'review_id':str(row.pk),'review_digest':fingerprint(body),'confirmed_by':body['reviewed_by']}:raise AccountingError('Confirmation origin changed.')
    current=None
    try:current=assess(company,body['account_id'],body['period'],[],[],allow_empty=True)
    except (AccountingError,ObjectDoesNotExist,ValueError,TypeError):pass
    valid=current==body['assessment'] and current is not None and current['eligible_for_period_reconciliation']
    return {'schema':'sgacd-empty-bank-period-v1','company_id':str(company.pk),'account_id':body['account_id'],'request_id':body['request_id'],'review_id':str(row.pk),'assessment':body['assessment'],'source_current':valid,'historically_confirmed':applied is not None,'period_reconciled':bool(applied and valid),'requires_review':not valid,'expires_at':body['expires_at'],'read_only':True,'confirmations_restored':False,'bank_verified':False,'ledger_written':False,'money_transferred':False}


@transaction.atomic
def review(company_id,*,actor,request_id,account_id,period,no_bank_movements,confirmed):
    company,user=bank._context(company_id,actor)
    if not isinstance(request_id,str) or str(UUID(request_id))!=request_id or no_bank_movements is not True or confirmed is not True:raise AccountingError('Explicit zero-activity declaration and first confirmation required.')
    account_id=str(UUID(str(account_id)))
    assessment=assess(company,account_id,period,[],[],allow_empty=True)
    if not assessment['eligible_for_period_reconciliation']:raise AccountingError('An empty bank period requires matching balances and no posted cash movements.')
    key=uuid5(NS,REVIEW+':'+str(company.pk)+':'+request_id)
    old=OutboxEvent.objects.filter(pk=key).first()
    if old:
        body=checked(company,old,REVIEW)
        if body['account_id']!=account_id or body['period']!=period or body['assessment']!=assessment or body['reviewed_by']!=str(user.pk):raise AccountingError('Review identity reused with changed sources.')
        return result(company,old)
    body={'company_id':str(company.pk),'account_id':account_id,'request_id':request_id,'period':period,'assessment':assessment,'reviewed_by':str(user.pk),'no_bank_movements':True,'expires_at':(timezone.now()+timedelta(minutes=15)).isoformat()}
    return result(company,store(company,REVIEW,body))


@transaction.atomic
def confirm(company_id,*,actor,review_id,confirmed):
    company,user=bank._context(company_id,actor)
    row=OutboxEvent.objects.filter(pk=UUID(str(review_id))).first();body=checked(company,row,REVIEW)
    if confirmed is not True or body['reviewed_by']!=str(user.pk):raise AccountingError('Separate second confirmation by the same owner required.')
    state=result(company,row)
    if state['historically_confirmed']:return state
    if not state['source_current'] or timezone.now()>=datetime.fromisoformat(body['expires_at']):raise AccountingError('Period changed or review expired; create a new review.')
    store(company,CONFIRMED,{'company_id':str(company.pk),'request_id':body['request_id'],'review_id':str(row.pk),'review_digest':fingerprint(body),'confirmed_by':str(user.pk)})
    return result(company,row)


@transaction.atomic
def state(company_id,*,actor,review_id):
    company,_=bank._context(company_id,actor)
    return result(company,OutboxEvent.objects.filter(pk=UUID(str(review_id))).first())
