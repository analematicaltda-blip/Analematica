"""A refund-bound transfer may execute only inside its accounting transaction."""
from contextvars import ContextVar
from contextlib import contextmanager
from uuid import UUID,uuid5
import hashlib
from rest_framework.exceptions import PermissionDenied
NS=UUID('2ec9cf73-4672-45c8-9733-32c264d53d11')
BOUND='wallet.commercial-refund.bound.v1'
CANCELLED='wallet.commercial-refund.cancelled.v1'
def cancellation_id(intent_id):return uuid5(NS,'cancelled:'+str(intent_id))
def cancelled(intent):
    if intent.state=='CANCELLED':return True
    from apps.core_erp.outbox_models import OutboxEvent
    return OutboxEvent.objects.filter(pk=cancellation_id(intent.pk)).exists() or OutboxEvent.objects.filter(event_type='commercial.wallet-refund.lifecycle.recorded.v1',payload__body__intent_id=str(intent.pk),payload__body__action='CANCEL').exists()
def require_active(intent):
    if cancelled(intent):raise PermissionDenied('La intención fue cancelada; se requieren otros procesos revisados para una nueva orden.')
_PREPARE=ContextVar('wallet_refund_prepare',default=None)
def request_key(company,reservation):
    # Reserved UUIDv8 application namespace; ordinary transfer requests cannot
    # use it. It survives missing Outbox indexes and prevents a downgrade.
    value=list('51acde01'+hashlib.sha256((str(company)+':'+str(reservation)).encode()).hexdigest()[8:32]);value[12]='8';value[16]='8';return UUID(hex=''.join(value))
def reserved(key):
    value=UUID(str(key));return value.version==8 and value.hex.startswith('51acde01')
@contextmanager
def prepare_permit(key,user):
    token=_PREPARE.set((str(key),str(user.pk)))
    try:yield
    finally:_PREPARE.reset(token)
def require_prepare(key,user):
    if reserved(key) and _PREPARE.get()!=(str(key),str(user.pk)):raise PermissionDenied('Identidad de solicitud reservada para devoluciones contables.')
_SCOPE=ContextVar('wallet_refund_scope',default=None)
def identity(intent_id):return uuid5(NS,str(intent_id))
@contextmanager
def permit(intent_id,user):
    token=_SCOPE.set((str(intent_id),str(user.pk)))
    try:yield
    finally:_SCOPE.reset(token)
def require(intent,user):
    from apps.core_erp.outbox_models import OutboxEvent
    row=OutboxEvent.objects.filter(pk=identity(intent.pk)).first()
    bound=OutboxEvent.objects.filter(event_type='commercial.wallet-refund.prepared.v1',payload__body__intent_id=str(intent.pk)).exists()
    if (bound or reserved(intent.idempotency_key)) and row is None:raise PermissionDenied('Falta la protección del reembolso; no se liberan fondos por evidencia ausente.')
    if row is not None:
        if row.event_type!=BOUND or _SCOPE.get()!=(str(intent.pk),str(user.pk)):raise PermissionDenied('Este reembolso se ejecuta desde el flujo contable de devolución; no mediante transferencia genérica.')
