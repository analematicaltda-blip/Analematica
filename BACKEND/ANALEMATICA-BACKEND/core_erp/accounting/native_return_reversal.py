"""Internal reviewed gate for full reversal after all native returns were corrected.
Never permits reversing return/correction journals or skipping source authorizations.
"""
from contextvars import ContextVar
from contextlib import contextmanager
from .exceptions import AccountingError
from .models import JournalEntry,AccountingEventReceipt
from apps.core_erp.outbox_models import OutboxEvent
_SCOPE=ContextVar('reviewed_native_return_reversal',default=None)
KINDS=('accounting.native-return.posted.v1','accounting.native-return.voided.v1')

def has_history(company,original_id):
    prefix='purchase-return:'+str(original_id)+':'
    return (JournalEntry.plain_objects.filter(tenant=company,is_posted=True,financial_event_id__startswith=prefix).exists()
        or AccountingEventReceipt.objects.filter(tenant=company,event_id__startswith=prefix).exists()
        or OutboxEvent.objects.filter(event_type__in=KINDS,payload__body__company_id=str(company.pk),payload__body__original_journal_id=str(original_id)).exists())

def snapshot(company,body,state):
    if not has_history(company,state['journal_id']):return None
    from apps.prestadores.mi_negocio.gestion_contable.compras import purchase_returns as returns
    original,verified=returns.original(company,body['document_id'])
    identity=original['source_binding']['identity']
    entries,used,head=returns.history(company,identity['invoice_id'],original,verified)
    if not entries or any(not row.get('reversed') for row in entries) or any(used.values()):raise AccountingError('Correct every active return before a full original reversal.')
    return {'document_id':body['document_id'],'invoice_id':identity['invoice_id'],'original_journal_id':state['journal_id'],'return_count':len(entries),'corrected_count':sum(bool(row.get('reversed')) for row in entries),'history_digest':head}

@contextmanager
def _permit(company,original_id,actor_id,verified_snapshot):
    if verified_snapshot is None:
        yield
        return
    token=_SCOPE.set((str(company.pk),str(original_id),str(actor_id),verified_snapshot))
    try:yield
    finally:_SCOPE.reset(token)

def require(company,original,actor_id):
    if (original.financial_event_id and original.financial_event_id.startswith('purchase-return:')
            or AccountingEventReceipt.objects.filter(tenant=company,journal_id=original.pk,event_id__startswith='purchase-return:').exists()
            or OutboxEvent.objects.filter(event_type__in=KINDS,payload__body__company_id=str(company.pk),payload__body__journal_id=str(original.pk)).exists()):raise AccountingError('Return/correction journals require their dedicated reviewed flow.')
    if not has_history(company,original.pk):return
    permit=_SCOPE.get()
    if permit is None or permit[:3]!=(str(company.pk),str(original.pk),str(actor_id)):raise AccountingError('Reviewed full reversal required after native return corrections.')
    from .commercial_tax_posting import original_state
    _,body,_,state=original_state(company,permit[3]['document_id'])
    if snapshot(company,body,state)!=permit[3]:raise AccountingError('Return reconciliation changed; obtain two new confirmations.')
