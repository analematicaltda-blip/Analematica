"""Serialize supported account/period bulk writes before acquiring their rows."""
from django.db import models,transaction
from apps.core_erp.base_models import TenantQuerySet,TenantManager
from apps.core_erp.tenancy.utils import get_current_tenant_id
from .exceptions import AccountingError


def companies(identifiers):
    from apps.core_erp.tenancy.models import Tenant
    identifiers=set(identifiers)
    if None in identifiers:raise AccountingError('Accounting bulk state requires explicit companies.')
    found=list(Tenant.objects.select_for_update().filter(pk__in=identifiers).order_by('pk'))
    if len(found)!=len(identifiers):raise AccountingError('Accounting company unavailable.')

class StateQuerySet(TenantQuerySet):
    def _companies(self):
        owners=self.order_by().values_list('tenant_id',flat=True).distinct()
        owners.query.select_for_update=False  # Read owner IDs before acquiring company/row locks.
        companies(owners)

    @transaction.atomic
    def update(self,**kwargs):
        if {'tenant','tenant_id'}&set(kwargs):raise AccountingError('Accounting company cannot be reassigned by bulk update.')
        self._companies()
        from .state_lock import ACCOUNT_HASH_FIELDS
        if self.model._meta.model_name=='account' and ACCOUNT_HASH_FIELDS & set(kwargs):
            from .models import LedgerEntry
            if LedgerEntry.plain_objects.filter(account_id__in=self.values('pk'),journal_entry__is_posted=True).exists():
                raise AccountingError('Bulk changes of posted account identity are not permitted.')
        return super().update(**kwargs)

    @transaction.atomic
    def delete(self):
        self._companies()
        return super().delete()

    @transaction.atomic
    def bulk_update(self,objs,fields,batch_size=None):
        objs=list(objs)
        if {'tenant','tenant_id'}&set(fields):raise AccountingError('Accounting company cannot be reassigned by bulk update.')
        self.model.plain_objects.filter(pk__in=[obj.pk for obj in objs])._companies()
        return super().bulk_update(objs,fields,batch_size=batch_size)

    @transaction.atomic
    def bulk_create(self,objs,*args,**kwargs):
        objs=list(objs)
        if kwargs.get('update_conflicts') or len(args)>2 and args[2]:raise AccountingError('Review existing accounting state explicitly instead of bulk upsert.')
        companies(obj.tenant_id for obj in objs)
        return super().bulk_create(objs,*args,**kwargs)

    @transaction.atomic
    def update_or_create(self,defaults=None,create_defaults=None,**kwargs):
        if {'tenant','tenant_id'}&set(defaults or {}):raise AccountingError('Accounting company cannot be reassigned.')
        self.filter(**kwargs)._companies()
        return super().update_or_create(defaults=defaults,create_defaults=create_defaults,**kwargs)

class StateManager(models.Manager.from_queryset(StateQuerySet)):
    pass

class ScopedStateManager(TenantManager.from_queryset(StateQuerySet)):
    def get_queryset(self):
        queryset=StateQuerySet(self.model,using=self._db,hints=self._hints)
        tenant=get_current_tenant_id()
        return queryset.filter(tenant_id=tenant) if tenant else queryset.none()
