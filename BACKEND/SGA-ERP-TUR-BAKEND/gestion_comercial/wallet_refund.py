"""Funded commercial refunds into an opted-in personal wallet and company ledger.
Same database only. Reuses transfer limits and native device approvals. No bank
withdrawal, new money, identity guessing or silent fiscal adjustment.
"""
from dataclasses import dataclass
from datetime import datetime,timedelta
from decimal import Decimal
from uuid import UUID,uuid5
from django.conf import settings
from django.db import transaction,router
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.models import Account,LedgerEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.exceptions import AccountingError
from apps.wallet.models import Wallet,WalletTransferIntent,WalletMovimiento
from apps.wallet.services import internal_transfer,refund_guard
from apps.wallet.services.access_policy import require_wallet_access,personal_signup,PERSONAL_TYPES
from apps.wallet.services.wallet_service import WalletOperationUnavailable
from . import cancellation_policies as policy,refund_liability
BINDING='commercial.wallet-refund.prepared.v1'
POSTED='commercial.wallet-refund.posted.v1'
@dataclass(frozen=True)
class VerifiedRefundBeneficiary:
    company_id:UUID
    customer_id:UUID
    wallet_id:UUID
    user_id:int
    reservation_id:UUID
    accepts_wallet_refund:bool
    evidence_digest:str
    checked_at:datetime
    valid_until:datetime

def enabled():
    if not getattr(settings,'WALLET_COMMERCIAL_REFUNDS_ENABLED',False):raise WalletOperationUnavailable('Falta habilitar el adaptador conciliado de devoluciones a billetera.')
    for model in (Wallet,WalletTransferIntent,WalletMovimiento,LedgerEntry,OutboxEvent):
        if router.db_for_write(model)!='default':raise WalletOperationUnavailable('Abono y asiento requieren la misma base transaccional; no hay atomicidad entre bases distintas.')

def context(actor,provider_id,reservation_id):
    enabled();user,provider,company=policy.context(actor,provider_id);r=policy.reservation(company,reservation_id);state=policy.case_state(actor=user,provider_id=provider.pk,reservation_id=reservation_id)
    if state['registered'] is None or Decimal(state['registered']['calculation']['refund_net'])<=0:raise AccountingError('Se requiere propuesta positiva de devolución registrada.')
    return user,provider,company,r,state['registered']

def store(kind,company,provider,identity,body):
    return OutboxEvent.objects.create(id=policy.key(kind,company,identity),event_type=kind,domain='commercial',aggregate_root=str(company.pk),version=1,payload={'company_id':str(company.pk),'provider_id':str(provider.pk),'body':body,'digest':fingerprint(body)})
def read(kind,company,provider,reservation_id):
    row=OutboxEvent.objects.filter(pk=policy.key(kind,company,reservation_id)).first()
    if row is None:return None
    if row.event_type!=kind or row.domain!='commercial' or row.aggregate_root!=str(company.pk) or row.version!=1 or set(row.payload)!={'company_id','provider_id','body','digest'} or row.payload['company_id']!=str(company.pk) or row.payload['provider_id']!=str(provider.pk) or fingerprint(row.payload['body'])!=row.payload['digest']:raise AccountingError('Evidencia de devolución a billetera alterada.')
    return row.payload['body']

def parties(user,company,r,source_id,destination_id):
    wallets={str(w.pk):w for w in Wallet.objects.select_for_update().filter(pk__in=[UUID(str(source_id)),UUID(str(destination_id))]).order_by('pk')}
    if len(wallets)!=2:raise AccountingError('Se requieren dos billeteras existentes y distintas.')
    source,destination=wallets[str(source_id)],wallets[str(destination_id)];require_wallet_access(user,source)
    if source.owner_type!='CORPORATIVO' or source.owner_id!=str(company.pk) or source.currency!='COP' or destination.currency!='COP' or source.estado!='ACTIVO' or destination.estado!='ACTIVO' or destination.owner_type not in PERSONAL_TYPES:raise AccountingError('Empresa y cliente deben tener billeteras COP activas correctamente vinculadas.')
    verifier=getattr(settings,'WALLET_REFUND_BENEFICIARY_VERIFIER',None)
    if not callable(verifier):raise WalletOperationUnavailable('Falta verificar el vínculo entre cliente de reserva y titular de billetera; no se deduce del correo ni del ID enviado.')
    proof=verifier(company,r,destination);now=timezone.now()
    if type(proof)is not VerifiedRefundBeneficiary or proof.reservation_id!=r.pk or proof.accepts_wallet_refund is not True or proof.company_id!=company.pk or proof.customer_id!=r.customer_id or proof.wallet_id!=destination.pk or proof.user_id!=destination.user_id or not timezone.is_aware(proof.checked_at) or not timezone.is_aware(proof.valid_until) or not now-timedelta(minutes=5)<=proof.checked_at<=now<proof.valid_until<=proof.checked_at+timedelta(minutes=5):raise PermissionDenied('Titular de billetera no verificado para ese cliente y empresa.')
    policy.digest(proof.evidence_digest)
    from django.contrib.auth import get_user_model
    recipient=get_user_model().objects.filter(pk=proof.user_id,is_active=True).first()
    if recipient is None or not personal_signup(recipient):raise PermissionDenied('El cliente debe darse de alta expresamente en su billetera personal.')
    return source,destination,proof

def asset(company,wallet):
    identifier=wallet.metadata.get('accounting_asset_account_id');a=Account.plain_objects.select_for_update().filter(pk=UUID(str(identifier)),tenant=company,chart_of_accounts__tenant=company,is_active=True,type='ASSET').first()
    if a is None:raise AccountingError('La billetera empresarial requiere cuenta de activo conciliada; no se acredita una cuenta bancaria por defecto.')
    lines=list(LedgerEntry.plain_objects.filter(tenant=company,account=a,journal_entry__tenant=company,journal_entry__is_posted=True).select_related('journal_entry').order_by('pk')[:2001])
    if len(lines)>2000:raise AccountingError('Se requiere conciliación de la historia del activo de billetera.')
    balance=Decimal('0.00');checked=set()
    for line in lines:
        j=line.journal_entry
        if j.pk not in checked:
            if j.hash_version!='v2' or j.currency!='COP' or j.base_currency!='COP' or j.exchange_rate!=1 or j.date>timezone.localdate() or not j.posted_at or j.posted_at>timezone.now() or j.compute_hash()!=j.system_hash:raise AccountingError('Activo de billetera requiere reconciliación de integridad.')
            checked.add(j.pk)
        if line.currency!='COP' or line.amount_base!=line.debit_amount+line.credit_amount or line.amount_transaction!=line.amount_base:raise AccountingError('Valoración del activo de billetera incompatible.')
        balance+=line.debit_amount-line.credit_amount
    return a,balance

def flags(company,provider):return {**policy.flags(company,provider),'bank_transfer_executed':False,'network_called':False,'confirmations_restored':False}

def binding(company,provider,reservation_id):
    b=read(BINDING,company,provider,reservation_id)
    if b is None:raise AccountingError('Prepara primero la devolución a billetera.')
    guard=OutboxEvent.objects.filter(pk=refund_guard.identity(b['intent_id'])).first()
    if guard is None or guard.event_type!=refund_guard.BOUND or guard.domain!='commercial' or guard.aggregate_root!=str(company.pk) or guard.payload!={'binding_id':str(policy.key(BINDING,company,reservation_id)),'binding_digest':fingerprint(b)}:raise AccountingError('Protección de transferencia contable ausente o alterada.')
    return b

@transaction.atomic
def prepare_wallet_refund(*,actor,provider_id,reservation_id,source_wallet_id,destination_wallet_id,liability_line_id,evidence_digest,confirmed):
    user,provider,company,r,proposal=context(actor,provider_id,reservation_id);policy.digest(evidence_digest)
    if confirmed is not True:raise AccountingError('Revisión explícita de destino, obligación y fondos requerida.')
    old=read(BINDING,company,provider,reservation_id)
    if old:
        if any(old[k]!=v for k,v in {'source_wallet_id':source_wallet_id,'destination_wallet_id':destination_wallet_id,'liability_line_id':liability_line_id,'evidence_digest':evidence_digest,'proposal_digest':fingerprint(proposal)}.items()):raise AccountingError('La devolución ya tiene un destino y fuente vinculados.')
        binding(company,provider,reservation_id);return {**flags(company,provider),'binding':old,'replayed':True}
    from . import refund_orders
    gateway_order=OutboxEvent.objects.filter(pk=policy.key(refund_orders.ORDER,company,reservation_id)).first()
    if gateway_order and refund_orders.read(gateway_order,refund_orders.ORDER,company,provider)['status']!='BLOCKED_BOLD_VERIFICATION':raise AccountingError('Existe una orden bancaria en curso o completada; concilia antes de cambiar el destino.')
    source,destination,proof=parties(user,company,r,source_wallet_id,destination_wallet_id);amount=proposal['calculation']['refund_net'];a,balance=asset(company,source)
    if balance!=source.saldo_disponible+source.saldo_bloqueado+source.saldo_en_proceso or balance<Decimal(amount):raise AccountingError('Activo conciliado insuficiente para devolver fondos.')
    line=refund_liability.source_line(company,liability_line_id,amount,timezone.localdate(),available=True)
    key=refund_guard.request_key(company.pk,reservation_id)
    with refund_guard.prepare_permit(key,user):intent=internal_transfer.prepare(user,source.pk,destination.pk,amount,key)
    intent.consent_by_id=proof.user_id;intent.consent_digest=intent.digest;intent.consent_at=proof.checked_at
    intent.save(update_fields=['consent_by_id','consent_digest','consent_at'])
    body={'reservation_id':reservation_id,'customer_id':str(r.customer_id),'source_wallet_id':str(source.pk),'destination_wallet_id':str(destination.pk),'recipient_user_id':proof.user_id,'recipient_evidence_digest':proof.evidence_digest,'amount':amount,'currency':'COP','proposal_digest':fingerprint(proposal),'liability_line_id':str(line.pk),'liability_account_id':str(line.account_id),'liability_journal_hash':line.journal_entry.system_hash,'asset_account_id':str(a.pk),'evidence_digest':evidence_digest,'actor_id':str(user.pk),'intent_id':str(intent.pk),'intent_digest':intent.digest,'expires_at':intent.expires_at.isoformat()}
    store(BINDING,company,provider,reservation_id,body);OutboxEvent.objects.create(id=refund_guard.identity(intent.pk),event_type=refund_guard.BOUND,domain='commercial',aggregate_root=str(company.pk),version=1,payload={'binding_id':str(policy.key(BINDING,company,reservation_id)),'binding_digest':fingerprint(body)})
    return {**flags(company,provider),'binding':body,'replayed':False}

@transaction.atomic
def review_wallet_refund(*,actor,provider_id,reservation_id,device_proof,confirmed):
    user,provider,company,r,proposal=context(actor,provider_id,reservation_id);b=binding(company,provider,reservation_id)
    if confirmed is not True or b['actor_id']!=str(user.pk) or b['proposal_digest']!=fingerprint(proposal):raise AccountingError('Primera autorización financiera del titular requerida.')
    _,_,proof=parties(user,company,r,b['source_wallet_id'],b['destination_wallet_id'])
    if proof.user_id!=b['recipient_user_id'] or proof.evidence_digest!=b['recipient_evidence_digest']:raise AccountingError('El consentimiento cambió; revisión nueva requerida.')
    approved=WalletTransferIntent.objects.select_for_update().get(pk=b['intent_id'])
    approved.consent_by_id=proof.user_id;approved.consent_digest=approved.digest;approved.consent_at=proof.checked_at
    approved.save(update_fields=['consent_by_id','consent_digest','consent_at'])
    intent,token=internal_transfer.review(user,b['intent_id'],b['intent_digest'],device_proof)
    return {**flags(company,provider),'intent_id':str(intent.pk),'state':intent.state,'confirmation':token}

@transaction.atomic
def execute_wallet_refund(*,actor,provider_id,reservation_id,confirmation,device_proof,confirmed):
    user,provider,company,r,proposal=context(actor,provider_id,reservation_id);b=binding(company,provider,reservation_id)
    if confirmed is not True or b['actor_id']!=str(user.pk) or b['proposal_digest']!=fingerprint(proposal):raise AccountingError('Segunda autorización financiera del mismo administrador requerida.')
    source,destination,proof=parties(user,company,r,b['source_wallet_id'],b['destination_wallet_id'])
    old=read(POSTED,company,provider,reservation_id)
    if old:return {**flags(company,provider),'settlement':verify(company,provider,reservation_id),'replayed':True}
    line=refund_liability.source_line(company,b['liability_line_id'],b['amount'],timezone.localdate(),available=True);a,balance=asset(company,source)
    if str(a.pk)!=b['asset_account_id'] or line.journal_entry.system_hash!=b['liability_journal_hash'] or balance!=source.saldo_disponible+source.saldo_bloqueado+source.saldo_en_proceso or balance<Decimal(b['amount']) or proof.user_id!=b['recipient_user_id'] or proof.evidence_digest!=b['recipient_evidence_digest']:raise AccountingError('Fuente contable, destinatario o fondos cambiaron tras la revisión.')
    with refund_guard.permit(b['intent_id'],user):intent=internal_transfer.execute(user,b['intent_id'],b['intent_digest'],confirmation,device_proof)
    intent.transaction.metadata={**intent.transaction.metadata,'purpose':'COMMERCIAL_REFUND','reservation_id':reservation_id,'company_id':str(company.pk)};intent.transaction.save(update_fields=['metadata'])
    j=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=timezone.localdate(),description='Reembolso a billetera, reserva '+reservation_id,lines_data=[{'account':line.account,'debit':b['amount']},{'account':a,'credit':b['amount']}],actor=user,idempotency_key='wallet-refund:'+str(policy.key(POSTED,company,reservation_id)))
    result={'reservation_id':reservation_id,'intent_id':b['intent_id'],'binding_digest':fingerprint(b),'transaction_id':str(intent.transaction_id),'journal_id':str(j.pk),'journal_hash':j.system_hash,'amount':b['amount'],'currency':'COP','status':'CREDITED_TO_CUSTOMER_WALLET'};store(POSTED,company,provider,reservation_id,result);store(refund_liability.USED_SOURCE,company,provider,b['liability_line_id'],{'reservation_id':reservation_id,'journal_id':str(j.pk)})
    return {**flags(company,provider),'settlement':verify(company,provider,reservation_id),'replayed':False,'ledger_written':True,'money_transferred':True}

def verify(company,provider,reservation_id):
    result=read(POSTED,company,provider,reservation_id)
    if result is None:return None
    b=binding(company,provider,reservation_id)
    claim=read(refund_liability.USED_SOURCE,company,provider,b['liability_line_id'])
    if claim!={'reservation_id':reservation_id,'journal_id':result['journal_id']}:raise AccountingError('Reserva de obligación ausente o alterada.')
    intent=WalletTransferIntent.objects.filter(pk=b['intent_id'],state='EXECUTED',transaction_id=result['transaction_id']).first()
    if intent is None or result['binding_digest']!=fingerprint(b) or intent.digest!=b['intent_digest']:raise AccountingError('Abono de billetera no verificable.')
    if str(intent.source_id)!=b['source_wallet_id'] or str(intent.destination_id)!=b['destination_wallet_id'] or intent.amount!=Decimal(b['amount']) or intent.currency!='COP' or intent.digest!=internal_transfer.fingerprint(intent.source_id,intent.destination_id,intent.amount,intent.currency) or intent.transaction.estado!='COMPLETADA' or intent.transaction.monto_total!=intent.amount or intent.transaction.metadata.get('purpose')!='COMMERCIAL_REFUND' or intent.transaction.metadata.get('reservation_id')!=reservation_id:raise AccountingError('Transacción de devolución alterada.')
    movements=list(WalletMovimiento.objects.filter(transaccion_id=intent.transaction_id));expected={(b['source_wallet_id'],'PAGO'),(b['destination_wallet_id'],'INGRESO')}
    if len(movements)!=2 or {(str(m.wallet_id),m.tipo) for m in movements}!=expected or any(m.monto!=Decimal(b['amount']) or m.integrity_digest()!=m.hash_integridad for m in movements):raise AccountingError('Movimientos de billetera alterados.')
    from apps.core_erp.accounting.models import JournalEntry
    j=JournalEntry.plain_objects.filter(pk=result['journal_id'],tenant=company).first();refund_liability.journal(company,j)
    if j.system_hash!=result['journal_hash'] or j.financial_event_id!='wallet-refund:'+str(policy.key(POSTED,company,reservation_id)):raise AccountingError('Asiento de devolución a billetera alterado.')
    lines=list(LedgerEntry.plain_objects.filter(tenant=company,journal_entry=j))
    if sorted((str(l.account_id),format(l.debit_amount,'.2f'),format(l.credit_amount,'.2f')) for l in lines)!=sorted([(b['liability_account_id'],b['amount'],'0.00'),(b['asset_account_id'],'0.00',b['amount'])]):raise AccountingError('Líneas del asiento de devolución incompatibles.')
    return result

@transaction.atomic
def wallet_refund_state(*,actor,provider_id,reservation_id):
    _,provider,company,r,proposal=context(actor,provider_id,reservation_id);b=read(BINDING,company,provider,reservation_id)
    return {**flags(company,provider),'read_only':True,'binding':b,'settlement':verify(company,provider,reservation_id) if b else None}

@transaction.atomic
def wallet_refund_sources(*,actor,provider_id,reservation_id,after):
    user,provider,company,r,proposal=context(actor,provider_id,reservation_id)
    verifier=getattr(settings,'WALLET_REFUND_BENEFICIARY_VERIFIER',None);resolve=getattr(verifier,'wallet_id',None)
    if not callable(resolve):raise WalletOperationUnavailable('Falta resolver la billetera personal verificada del cliente; no se busca por correo ni se permite elegir un tercero.')
    destination=UUID(str(resolve(company,r)))
    candidates=list(Wallet.objects.filter(owner_type='CORPORATIVO',owner_id=str(company.pk),currency='COP',estado='ACTIVO').order_by('pk')[:21])
    if len(candidates)>20:raise AccountingError('Revisa el catálogo de billeteras empresariales.')
    sources=[]
    for source in candidates:
        parties(user,company,r,str(source.pk),str(destination));account,balance=asset(company,source)
        sources.append({'wallet_id':str(source.pk),'available':format(source.saldo_disponible,'.2f'),'reconciled':balance==source.saldo_disponible+source.saldo_bloqueado+source.saldo_en_proceso})
    rows=LedgerEntry.plain_objects.filter(tenant=company,account__tenant=company,account__chart_of_accounts__tenant=company,account__type='LIABILITY',account__is_active=True,credit_amount=Decimal(proposal['calculation']['refund_net']),debit_amount=0,journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__is_reversal=False).select_related('account','journal_entry').order_by('pk')
    if after is not None:rows=rows.filter(pk__gt=UUID(after))
    found=list(rows[:21])
    return {**flags(company,provider),'read_only':True,'source_wallets':sources,'destination_wallet_id':str(destination),'net_refund':proposal['calculation']['refund_net'],'liability_credits':[{'line_id':str(l.pk),'account_code':l.account.code,'date':l.journal_entry.date.isoformat(),'amount':format(l.credit_amount,'.2f')} for l in found[:20]],'next_after':str(found[19].pk) if len(found)>20 else None}
