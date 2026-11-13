"""Prevent generic ledger/hold endpoints from bypassing reviewed sales workflows."""
from contextvars import ContextVar
from contextlib import contextmanager
from .exceptions import AccountingError
_permit=ContextVar('commercial_sale_ledger_permit',default=None)
@contextmanager
def permit(company,sale):
    token=_permit.set((str(company),str(sale)))
    try:yield
    finally:_permit.reset(token)
def require(company,key):
    if isinstance(key,str) and key.startswith('commercial-sale:'):
        sale=key.rsplit(':',1)[-1]
        if _permit.get()!=(str(company),sale):raise AccountingError('Reviewed commercial sale workflow required.')
def require_reversal(company,journal):require(company,journal.financial_event_id)

def require_hold_release(hold):
    from django.apps import apps
    from django.db import connection
    from django.db.models import Q
    tables=set(connection.introspection.table_names())
    for label in ('gestion_comercial','admin_plataforma'):
        try:model=apps.get_model(label,'CommercialSale')
        except LookupError:continue
        if model._meta.db_table not in tables:continue
        query=Q()
        for index in range(10):query|=Q(**{'document__operation_refs__'+str(index)+'__hold_id':str(hold.pk)})
        for sale in model.objects.filter(provider_ref=str(hold.provider_id)).filter(query):require(sale.scope,'commercial-sale:'+str(sale.pk))
