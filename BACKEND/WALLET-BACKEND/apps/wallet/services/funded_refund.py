"""Funded reversal of an executed internal transfer with a same-DB journal.

Existing corporate funds only. No bank payment, deposit, treasury credit or
recipient enrollment is invented. Generic transfer APIs cannot create a refund.
"""
from uuid import UUID
from datetime import date
from django.db import transaction, router
from django.utils import timezone
from ..models import Wallet, WalletTransferIntent, WalletTransaccion, WalletMovimiento
from . import internal_transfer as transfers


def accounting_context(user,provider_id,source):
    from apps.prestadores.mi_negocio.gestion_contable.compras.native_purchase import context
    _,provider,company=context(user,provider_id)
    from .access_policy import require_wallet_access, PERSONAL_TYPES
    require_wallet_access(user,source)
    if source.owner_type in PERSONAL_TYPES or source.owner_id!=str(provider.pk):
        raise transfers.TransferConflict('Se requiere billetera empresarial vinculada a la empresa verificada.')
    from apps.core_erp.accounting.models import JournalEntry, LedgerEntry
    from apps.core_erp.outbox_models import OutboxEvent
    if any(router.db_for_write(model) not in {None,'default'} for model in (Wallet,WalletTransferIntent,WalletTransaccion,WalletMovimiento,JournalEntry,LedgerEntry,OutboxEvent)):
        raise transfers.TransferConflict('El reembolso exige billetera y asiento en la misma base transaccional.')
    return company


def validate_execution(user,intent):
    from apps.core_erp.accounting.return_policy import quote
    from apps.core_erp.accounting.models import Account
    purpose=intent.purpose
    if set(purpose)!={'kind','provider_id','original_intent_id','policy','scheduled_date','requested_date','debit_account_id','credit_account_id'} or purpose['kind']!='FUNDED_REFUND_V1':
        raise transfers.TransferConflict('Contrato de reembolso inválido.')
    company=accounting_context(user,purpose['provider_id'],intent.source)
    original=WalletTransferIntent.objects.select_for_update().select_related('transaction').filter(pk=purpose['original_intent_id'],state='EXECUTED',source_id=intent.destination_id,destination_id=intent.source_id,currency='COP',purpose={}).first()
    if original is None or original.transaction is None or original.transaction.estado!='COMPLETADA' or original.transaction.monto_total!=original.amount or original.digest!=transfers.fingerprint(original.source_id,original.destination_id,original.amount,original.currency) or original.transaction.metadata!={'kind':'INTERNAL_TRANSFER_V1','currency':original.currency,'intent_id':str(original.pk)} or intent.currency!='COP':
        raise transfers.TransferConflict('Pago interno original completo y contraparte exacta requeridos.')
    movements=list(original.transaction.movimientos.all())
    if len(movements)!=2 or {(m.wallet_id,m.tipo,m.monto) for m in movements}!={(original.source_id,'PAGO',original.amount),(original.destination_id,'INGRESO',original.amount)} or any(m.hash_integridad!=m.integrity_digest() for m in movements):
        raise transfers.TransferConflict('Los movimientos originales requieren conciliación.')
    result=quote(purpose['policy'],paid=format(original.amount,'.2f'),scheduled_date=purpose['scheduled_date'],requested_date=purpose['requested_date'])
    used=sum((x.amount for x in WalletTransferIntent.objects.filter(state='EXECUTED',purpose__original_intent_id=str(original.pk)).exclude(pk=intent.pk)),transfers.Decimal(0))
    if used+intent.amount>transfers.Decimal(result['maximum_refund']):raise transfers.TransferConflict('El reembolso acumulado excede el pago y la política autorizada.')
    if purpose['requested_date']>timezone.localdate().isoformat():raise transfers.TransferConflict('Fecha futura de solicitud no admitida.')
    if purpose['debit_account_id']==purpose['credit_account_id']:raise transfers.TransferConflict('Cuentas contables distintas requeridas.')
    for identifier in [purpose['debit_account_id'],purpose['credit_account_id']]:
        if not Account.plain_objects.filter(pk=identifier,tenant=company,chart_of_accounts__tenant=company,is_active=True).exists():raise transfers.TransferConflict('Cuenta contable no disponible en la empresa.')
    return company


@transaction.atomic
def prepare(user, *, provider_id, original_intent_id, source_id, destination_id, amount, key, policy, scheduled_date, debit_account_id, credit_account_id):
    transfers.principal(user)
    source_id=UUID(str(source_id));destination_id=UUID(str(destination_id))
    purpose={'kind':'FUNDED_REFUND_V1','provider_id':str(UUID(str(provider_id))),'original_intent_id':str(UUID(str(original_intent_id))),
        'policy':policy,'scheduled_date':scheduled_date,'requested_date':timezone.localdate().isoformat(),
        'debit_account_id':str(UUID(str(debit_account_id))),'credit_account_id':str(UUID(str(credit_account_id)))}
    old=WalletTransferIntent.objects.filter(requested_by_id=user.pk,idempotency_key=key).first()
    if old:
        accounting_context(user,provider_id,old.source)
        # A retry on another date preserves the original request date.
        purpose['requested_date']=old.purpose.get('requested_date',purpose['requested_date'])
        if old.purpose!=purpose or old.digest!=transfers.fingerprint(source_id,destination_id,transfers.money(amount),old.currency,purpose):raise transfers.TransferConflict('Clave de reembolso reutilizada.')
        return old
    intent=transfers.prepare(user,source_id,destination_id,amount,key)
    intent.purpose=purpose;intent.digest=transfers.fingerprint(intent.source_id,intent.destination_id,intent.amount,intent.currency,purpose)
    validate_execution(user,intent)
    intent.save(update_fields=['purpose','digest'])
    return intent


def post_accounting(user,intent,tx):
    from apps.core_erp.accounting.ledger_engine import LedgerEngine
    from apps.core_erp.accounting.models import Account
    company=validate_execution(user,intent);p=intent.purpose
    entry=LedgerEngine.post_lines(tenant_id=company.pk,actor=user,entry_date=date.fromisoformat(p['requested_date']),
        description='Funded internal wallet refund',idempotency_key='wallet-refund:'+str(intent.pk),
        lines_data=[{'account':Account.plain_objects.get(pk=p['debit_account_id'],tenant=company),'debit':format(intent.amount,'.2f')},
                    {'account':Account.plain_objects.get(pk=p['credit_account_id'],tenant=company),'credit':format(intent.amount,'.2f')}])
    tx.metadata={**tx.metadata,'kind':'FUNDED_REFUND_V1','journal_id':str(entry.pk),'company_id':str(company.pk),'original_intent_id':p['original_intent_id']}
    tx.save(update_fields=['metadata'])



def verify_posted(intent):
    from apps.core_erp.accounting.models import JournalEntry, LedgerEntry, AccountingEventReceipt
    tx=intent.transaction
    if tx is None or tx.metadata.get('kind')!='FUNDED_REFUND_V1' or tx.metadata.get('intent_id')!=str(intent.pk) or tx.monto_total!=intent.amount or tx.estado!='COMPLETADA':
        raise transfers.TransferConflict('Falta prueba de origen del reembolso; no se reconstruye un pago.')
    entry=JournalEntry.plain_objects.filter(pk=tx.metadata.get('journal_id'),tenant_id=tx.metadata.get('company_id'),is_posted=True,financial_event_id='wallet-refund:'+str(intent.pk)).first()
    if entry is None or entry.compute_hash()!=entry.system_hash or not AccountingEventReceipt.objects.filter(tenant_id=entry.tenant_id,event_id='wallet-refund:'+str(intent.pk),journal=entry).exists():
        raise transfers.TransferConflict('El asiento de reembolso requiere conciliación.')
    expected=sorted([(intent.purpose['debit_account_id'],intent.amount,transfers.Decimal(0)),(intent.purpose['credit_account_id'],transfers.Decimal(0),intent.amount)])
    actual=sorted((str(l.account_id),l.debit_amount,l.credit_amount) for l in LedgerEntry.plain_objects.filter(journal_entry=entry,tenant_id=entry.tenant_id))
    movements=list(tx.movimientos.all())
    if actual!=expected or len(movements)!=2 or {(m.wallet_id,m.tipo,m.monto) for m in movements}!={(intent.source_id,'PAGO',intent.amount),(intent.destination_id,'INGRESO',intent.amount)} or any(m.hash_integridad!=m.integrity_digest() for m in movements):
        raise transfers.TransferConflict('Los movimientos o el asiento del reembolso cambiaron.')
