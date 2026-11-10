"""Append-only cancellation and expiry renewal, never financial approvals.
Renewal invalidates every old token/challenge and requires two NEW financial
signatures. Cancellation is terminal for the bound intent; it moves no balance.
"""
from datetime import datetime,timedelta
from django.db import transaction
from django.utils import timezone
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.wallet.models import WalletTransferIntent,WalletDeviceChallenge
from apps.wallet.services import refund_guard
from . import wallet_refund as refund
from . import cancellation_policies as policy
REVIEW='commercial.wallet-refund.lifecycle.reviewed.v1'
RECORDED='commercial.wallet-refund.lifecycle.recorded.v1'

def _read(row,kind,company,provider,identity):
    if row is None:raise AccountingError('Evidencia de ciclo de devolución ausente.')
    p=row.payload
    if row.pk!=policy.key(kind,company,identity) or row.event_type!=kind or row.domain!='commercial' or row.aggregate_root!=str(company.pk) or row.version!=1 or set(p)!={'company_id','provider_id','body','digest'} or p['company_id']!=str(company.pk) or p['provider_id']!=str(provider.pk) or not isinstance(p['body'],dict) or p['digest']!=fingerprint(p['body']):raise AccountingError('Evidencia de ciclo de devolución alterada.')
    return p['body']

def history(company,provider,reservation_id):
    rows=list(OutboxEvent.objects.filter(event_type=RECORDED,payload__company_id=str(company.pk),payload__body__reservation_id=reservation_id).order_by('payload__body__revision')[:51]);result=[];previous=None
    if len(rows)>50:raise AccountingError('Historial de renovación requiere archivo revisado.')
    for row in rows:
        revision=len(result)+1;b=_read(row,RECORDED,company,provider,reservation_id+':'+str(revision));review=OutboxEvent.objects.filter(pk=b['review_id']).first();r=_read(review,REVIEW,company,provider,b['request_id'])
        if b['revision']!=revision or b['previous_digest']!=(fingerprint(previous) if previous else None) or b['review_digest']!=fingerprint(r) or r['revision']!=revision or r['action']!=b['action'] or r['reservation_id']!=reservation_id or r['intent_id']!=b['intent_id']:raise AccountingError('Cadena del ciclo de devolución incompleta o alterada.')
        result.append(b);previous=b
    return result

def _snapshot(intent):
    return fingerprint({'id':str(intent.pk),'state':intent.state,'digest':intent.digest,'expires_at':intent.expires_at.isoformat(),'reviewed_at':intent.reviewed_at.isoformat() if intent.reviewed_at else None,'confirmation_hash':intent.confirmation_hash,'review_device_id':str(intent.review_device_id) if intent.review_device_id else None,'transaction_id':str(intent.transaction_id) if intent.transaction_id else None,'executed_at':intent.executed_at.isoformat() if intent.executed_at else None})

def _context(actor,provider_id,reservation_id):
    refund.enabled();user,provider,company=policy.context(actor,provider_id);policy.reservation(company,reservation_id);b=refund.binding(company,provider,reservation_id)
    if b['actor_id']!=str(user.pk):raise AccountingError('El mismo administrador solicitante debe gestionar la intención.')
    intent=WalletTransferIntent.objects.select_for_update().filter(pk=b['intent_id'],requested_by_id=user.pk).first()
    if intent is None or intent.digest!=b['intent_digest'] or str(intent.source_id)!=b['source_wallet_id'] or str(intent.destination_id)!=b['destination_wallet_id'] or format(intent.amount,'.2f')!=b['amount']:raise AccountingError('Intención de devolución alterada.')
    return user,provider,company,b,intent

def _can_change(company,provider,reservation_id,intent,action):
    if action not in {'CANCEL','RENEW'} or intent.state not in {'PENDING','REVIEWED'} or intent.transaction_id or intent.executed_at or refund.read(refund.POSTED,company,provider,reservation_id):raise AccountingError('No se cancela ni renueva un abono ejecutado.')
    if refund_guard.cancelled(intent):raise AccountingError('La cancelación es definitiva para esta intención.')
    if action=='RENEW' and intent.expires_at>timezone.now():raise AccountingError('Solo se renuevan intenciones vencidas; una vigente conserva su plazo.')

def _renew_sources(user,provider,company,reservation_id,b):
    _,_,_,r,proposal=refund.context(user,provider.pk,reservation_id)
    if fingerprint(proposal)!=b['proposal_digest']:raise AccountingError('La propuesta cambió; no se renueva autorización sobre otra obligación.')
    source,_,proof=refund.parties(user,company,r,b['source_wallet_id'],b['destination_wallet_id']);a,balance=refund.asset(company,source)
    from decimal import Decimal
    if str(a.pk)!=b['asset_account_id'] or balance!=source.saldo_disponible+source.saldo_bloqueado+source.saldo_en_proceso or balance<Decimal(b['amount']) or source.saldo_disponible<Decimal(b['amount']) or proof.evidence_digest!=b['recipient_evidence_digest']:raise AccountingError('Fondos, consentimiento o activo cambiaron; revisa antes de renovar.')
    line=refund.refund_liability.source_line(company,b['liability_line_id'],b['amount'],timezone.localdate(),available=True)
    if line.journal_entry.system_hash!=b['liability_journal_hash']:raise AccountingError('La obligación cambió.')

def _result(company,provider,intent,hist):
    return {**refund.flags(company,provider),'intent_id':str(intent.pk),'status':'CANCELLED' if refund_guard.cancelled(intent) else intent.state,'expires_at':intent.expires_at.isoformat(),'lifecycle_revision':len(hist),'history':hist,'can_cancel':not refund_guard.cancelled(intent) and intent.state in {'PENDING','REVIEWED'} and not intent.transaction_id,'can_renew':not refund_guard.cancelled(intent) and intent.state in {'PENDING','REVIEWED'} and not intent.transaction_id and intent.expires_at<=timezone.now(),'financial_authorizations_restored':False}

@transaction.atomic
def review_wallet_refund_lifecycle(*,actor,provider_id,reservation_id,request_id,action,evidence_digest,expected_revision,confirmed):
    user,provider,company,b,intent=_context(actor,provider_id,reservation_id);policy.identifier(request_id);policy.digest(evidence_digest)
    if confirmed is not True or type(expected_revision) is not int:raise AccountingError('Primera revisión explícita de gestión requerida.')
    hist=history(company,provider,reservation_id);_can_change(company,provider,reservation_id,intent,action)
    if expected_revision!=len(hist) or len(hist)>=50:raise AccountingError('El ciclo cambió o agotó el historial acotado.')
    if action=='RENEW':_renew_sources(user,provider,company,reservation_id,b)
    body={'reservation_id':reservation_id,'intent_id':str(intent.pk),'request_id':request_id,'action':action,'revision':len(hist)+1,'previous_digest':fingerprint(hist[-1]) if hist else None,'binding_digest':fingerprint(b),'intent_snapshot_digest':_snapshot(intent),'reviewed_by':str(user.pk),'evidence_digest':evidence_digest}
    old=OutboxEvent.objects.filter(pk=policy.key(REVIEW,company,request_id)).first()
    if old:
        saved=_read(old,REVIEW,company,provider,request_id)
        if {k:v for k,v in saved.items() if k!='review_expires_at'}!=body:raise AccountingError('Identidad de revisión ya utilizada con otras condiciones.')
        return {**refund.flags(company,provider),'review_id':str(old.pk),'preview':saved}
    body['review_expires_at']=(timezone.now()+timedelta(minutes=15)).isoformat();row=refund.store(REVIEW,company,provider,request_id,body)
    return {**refund.flags(company,provider),'review_id':str(row.pk),'preview':body}

@transaction.atomic
def confirm_wallet_refund_lifecycle(*,actor,provider_id,reservation_id,review_id,confirmed):
    user,provider,company,b,intent=_context(actor,provider_id,reservation_id);policy.identifier(review_id);row=OutboxEvent.objects.filter(pk=review_id).first()
    if row is None:raise AccountingError('Revisión de gestión ausente.')
    request_id=row.payload.get('body',{}).get('request_id');r=_read(row,REVIEW,company,provider,request_id)
    if confirmed is not True or r['reviewed_by']!=str(user.pk) or r['reservation_id']!=reservation_id or r['intent_id']!=str(intent.pk) or r['binding_digest']!=fingerprint(b):raise AccountingError('Segunda confirmación del mismo solicitante requerida.')
    hist=history(company,provider,reservation_id)
    existing=next((x for x in hist if x['review_id']==review_id),None)
    if existing:return {**_result(company,provider,intent,hist),'replayed':True}
    _can_change(company,provider,reservation_id,intent,r['action'])
    if r['revision']!=len(hist)+1 or r['previous_digest']!=(fingerprint(hist[-1]) if hist else None) or r['intent_snapshot_digest']!=_snapshot(intent) or timezone.now()>=datetime.fromisoformat(r['review_expires_at']):raise AccountingError('Intención, revisión o ciclo cambiaron; revisa nuevamente.')
    if r['action']=='RENEW':_renew_sources(user,provider,company,reservation_id,b)
    now=timezone.now();invalidated=WalletDeviceChallenge.objects.filter(intent=intent,consumed_at__isnull=True,invalidated_at__isnull=True).update(invalidated_at=now)
    intent.confirmation_hash='';intent.review_device_id=None;intent.reviewed_at=None
    intent.consent_by_id=None;intent.consent_digest='';intent.consent_at=None
    if r['action']=='RENEW':intent.state='PENDING';intent.expires_at=now+timedelta(minutes=15)
    else:intent.state='CANCELLED'
    intent.save(update_fields=['confirmation_hash','review_device','reviewed_at','state','expires_at','consent_by_id','consent_digest','consent_at'])
    result={'reservation_id':reservation_id,'intent_id':str(intent.pk),'request_id':request_id,'review_id':review_id,'review_digest':fingerprint(r),'revision':r['revision'],'previous_digest':r['previous_digest'],'action':r['action'],'expires_at':intent.expires_at.isoformat(),'invalidated_challenges':invalidated,'performed_by':str(user.pk),'performed_at':now.isoformat()}
    proof=refund.store(RECORDED,company,provider,reservation_id+':'+str(r['revision']),result)
    if r['action']=='CANCEL':OutboxEvent.objects.create(id=refund_guard.cancellation_id(intent.pk),event_type=refund_guard.CANCELLED,domain='commercial',aggregate_root=str(company.pk),version=1,payload={'intent_id':str(intent.pk),'lifecycle_id':str(proof.pk),'lifecycle_digest':fingerprint(result)})
    return {**_result(company,provider,intent,hist+[result]),'replayed':False}

@transaction.atomic
def wallet_refund_lifecycle_state(*,actor,provider_id,reservation_id):
    _,provider,company,b,intent=_context(actor,provider_id,reservation_id);hist=history(company,provider,reservation_id)
    if intent.state=='EXECUTED' and refund.verify(company,provider,reservation_id) is None:raise AccountingError('Intención marcada ejecutada sin recibo contable; requiere reconciliación.')
    if refund_guard.cancelled(intent):
        marker=OutboxEvent.objects.filter(pk=refund_guard.cancellation_id(intent.pk)).first()
        if marker is None or not hist or hist[-1]['action']!='CANCEL' or marker.payload!={'intent_id':str(intent.pk),'lifecycle_id':str(policy.key(RECORDED,company,reservation_id+':'+str(hist[-1]['revision']))),'lifecycle_digest':fingerprint(hist[-1])}:raise AccountingError('Prueba de cancelación alterada.')
    elif hist and hist[-1]['action']=='CANCEL':raise AccountingError('Prueba de cancelación ausente; no se reactiva la intención.')
    return {**_result(company,provider,intent,hist),'read_only':True}
