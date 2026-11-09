"""Explicit opt-in keyset paging; legacy clients keep their bounded contract."""
from uuid import UUID
from django.db.models import Q
from .models import Account
from .exceptions import AccountingError

def _account_catalog(company,*,account_types,paged=None,after=None,search=None):
    if not company.is_active or company.state!='ACTIVE':raise AccountingError('Active accounting company required.')
    if paged not in (None,'1') or (paged is None and (after is not None or search is not None)):raise AccountingError('Use explicit paged mode for cursors or search.')
    query=Account.plain_objects.filter(tenant=company,chart_of_accounts__tenant=company,is_active=True,type__in=account_types)
    if search is not None:
        if not isinstance(search,str) or len(search)>100:raise AccountingError('Search must not exceed 100 characters.')
        query=query.filter(Q(code__icontains=search.strip())|Q(name__icontains=search.strip()))
    if after is not None:
        if not isinstance(after,str) or str(UUID(after))!=after:raise AccountingError('Canonical account cursor required.')
        query=query.filter(pk__gt=UUID(after))
    size=100 if paged=='1' else 500
    order=('pk',) if paged=='1' else ('code','pk')
    rows=list(query.order_by(*order).values('id','code','name','type')[:size+1])
    if paged is None and len(rows)>size:raise AccountingError('Use paged account selection for catalogs above 500 accounts.')
    return {'company_id':str(company.pk),'accounts':rows[:size],'read_only':True,'next_after':str(rows[size-1]['id']) if paged=='1' and len(rows)>size else None,'page_size':size,'ordering':'uuid' if paged=='1' else 'code_uuid','search':search or '', 'concurrent_insert_policy':'reload_to_include_rows_before_cursor'}


def recognition_catalog(company,*,paged=None,after=None,search=None):
    return _account_catalog(company,account_types=['ASSET','REVENUE','LIABILITY'],paged=paged,after=after,search=search)

def purchase_catalog(company,*,paged=None,after=None,search=None):
    return _account_catalog(company,account_types=['ASSET','EXPENSE','LIABILITY'],paged=paged,after=after,search=search)
