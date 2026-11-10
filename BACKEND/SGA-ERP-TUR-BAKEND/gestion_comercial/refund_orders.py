"""Durable Bold refund intentions; never mistake an intention for a bank receipt.
No undocumented refund URL, unsigned callback or client payload may settle money.
"""
from datetime import datetime,timedelta
from uuid import uuid5
import re
from django.db import transaction
from django.utils import timezone
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_intent import _money
from . import cancellation_policies as policy

REVIEW='commercial.refund-order.reviewed.v1'
ORDER='commercial.refund-order.authorized.v1'

def read(row,kind,company,provider):
    if row is None or row.event_type!=kind or row.domain!='commercial' or row.aggregate_root!=str(company.pk) or row.version!=1 or set(row.payload)!={'company_id','provider_id','body','digest'} or row.payload['company_id']!=str(company.pk) or row.payload['provider_id']!=str(provider.pk):raise AccountingError('Scoped refund order unavailable.')
    b=row.payload['body']
    identity=b['request_id'] if kind==REVIEW else b['reservation_id']
    if fingerprint(b)!=row.payload['digest'] or row.pk!=policy.key(kind,company,identity):raise AccountingError('Refund order origin changed.')
    return b

def write(kind,company,provider,b):
    identity=b['request_id'] if kind==REVIEW else b['reservation_id']
    return OutboxEvent.objects.create(id=policy.key(kind,company,identity),event_type=kind,domain='commercial',aggregate_root=str(company.pk),version=1,payload={'company_id':str(company.pk),'provider_id':str(provider.pk),'body':b,'digest':fingerprint(b)})

def source(actor,provider_id,reservation_id):
    user,provider,company=policy.context(actor,provider_id);r=policy.reservation(company,reservation_id);state=policy.case_state(actor=user,provider_id=provider.pk,reservation_id=reservation_id)
    if not state['registered'] or _money(state['registered']['calculation']['refund_net'])<=0:raise AccountingError('A recorded positive net refund proposal is required.')
    return user,provider,company,r,state['registered']

def flags(company,provider):return {**policy.flags(company,provider),'payment_executed':False,'network_called':False,'bank_receipt_verified':False,'confirmations_restored':False,'gateway':'BOLD'}

@transaction.atomic
def review_refund(*,actor,provider_id,reservation_id,request_id,original_payment_reference,evidence_digest,confirmed):
    user,provider,company,r,proposal=source(actor,provider_id,reservation_id)
    if OutboxEvent.objects.filter(pk=policy.key('commercial.wallet-refund.prepared.v1',company,reservation_id)).exists():raise AccountingError('Refund already bound to wallet; do not prepare a second payment channel.')
    policy.identifier(request_id);policy.digest(evidence_digest)
    if confirmed is not True or not isinstance(original_payment_reference,str) or not re.fullmatch('[A-Za-z0-9_-]{1,128}',original_payment_reference):raise AccountingError('First refund authorization and original Bold payment reference required.')
    # Keep only the original payment identifier digest in this unqualified queue.
    # A qualified gateway must resolve/verify the real transaction from its ledger.
    b={'reservation_id':reservation_id,'request_id':request_id,'proposal_digest':fingerprint(proposal),'customer_id':str(r.customer_id),'original_payment_digest':fingerprint({'gateway':'BOLD','payment_reference':original_payment_reference}),'evidence_digest':evidence_digest,'reviewed_by':str(user.pk),'amount':proposal['calculation']['refund_net'],'currency':'COP','gateway':'BOLD'}
    old=OutboxEvent.objects.filter(pk=policy.key(REVIEW,company,request_id)).first()
    if old:
        saved=read(old,REVIEW,company,provider)
        if {k:v for k,v in saved.items() if k!='expires_at'}!=b:raise AccountingError('Refund request identity changed.')
        return {**flags(company,provider),'review_id':str(old.pk),'preview':saved}
    if OutboxEvent.objects.filter(pk=policy.key(ORDER,company,reservation_id)).exists():raise AccountingError('Refund order already registered; recover instead of resubmitting.')
    b['expires_at']=(timezone.now()+timedelta(minutes=15)).isoformat();row=write(REVIEW,company,provider,b)
    return {**flags(company,provider),'review_id':str(row.pk),'preview':b}

@transaction.atomic
def authorize_refund(*,actor,provider_id,reservation_id,review_id,confirmed):
    user,provider,company,r,proposal=source(actor,provider_id,reservation_id)
    if OutboxEvent.objects.filter(pk=policy.key('commercial.wallet-refund.prepared.v1',company,reservation_id)).exists():raise AccountingError('Refund already bound to wallet; no second payment channel.')
    policy.identifier(review_id);b=read(OutboxEvent.objects.filter(pk=review_id).first(),REVIEW,company,provider)
    if confirmed is not True or b['reviewed_by']!=str(user.pk) or b['reservation_id']!=reservation_id:raise AccountingError('Second separate refund authorization by same administrator required.')
    old=OutboxEvent.objects.filter(pk=policy.key(ORDER,company,reservation_id)).first()
    if old:
        saved=read(old,ORDER,company,provider)
        if saved['review_id']!=review_id or saved['review_digest']!=fingerprint(b):raise AccountingError('Another refund order already registered.')
        return {**flags(company,provider),'order_id':str(old.pk),'order':saved,'replayed':True}
    if timezone.now()>=datetime.fromisoformat(b['expires_at']) or b['proposal_digest']!=fingerprint(proposal) or b['customer_id']!=str(r.customer_id):raise AccountingError('Refund review expired or source changed.')
    # No Bold refund contract/verified receipt exists yet. Persist an honest blocked
    # order, never create a PAGADA row or credit the bank from a declared payload.
    saved={'reservation_id':reservation_id,'review_id':review_id,'review_digest':fingerprint(b),'customer_id':b['customer_id'],'original_payment_digest':b['original_payment_digest'],'proposal_digest':b['proposal_digest'],'amount':b['amount'],'currency':'COP','gateway':'BOLD','status':'BLOCKED_BOLD_VERIFICATION','bank_receipt_id':None,'journal_id':None,'authorized_by':str(user.pk),'requires_authenticated_payment_and_refund':True,'accounting_plan':{'kind':'NOT_POSTED_SETTLEMENT_PLAN','debit_role':'customer_refund_payable','credit_role':'bold_clearing_or_bank','amount':b['amount'],'requires_qualified_accounts_original_funding_and_tax_adjustment':True}}
    row=write(ORDER,company,provider,saved)
    return {**flags(company,provider),'order_id':str(row.pk),'order':saved,'replayed':False}

@transaction.atomic
def refund_state(*,actor,provider_id,reservation_id):
    _,provider,company,r,proposal=source(actor,provider_id,reservation_id);row=OutboxEvent.objects.filter(pk=policy.key(ORDER,company,reservation_id)).first();b=read(row,ORDER,company,provider) if row else None
    if b:
        review=read(OutboxEvent.objects.filter(pk=b['review_id']).first(),REVIEW,company,provider)
        if b['review_digest']!=fingerprint(review) or b['proposal_digest']!=fingerprint(proposal) or b['amount']!=proposal['calculation']['refund_net']:raise AccountingError('Refund source changed.')
    return {**flags(company,provider),'reservation_id':reservation_id,'order_id':str(row.pk) if row else None,'order':b,'read_only':True}
