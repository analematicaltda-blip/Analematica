"""Company-first locking for supported accounting configuration model writes.

Raw SQL is an administrative escape hatch, not a lifecycle API.
Caller holds transaction.atomic; the ordering matches posting and reversal.
"""
def lock_state(instance):
    from apps.core_erp.tenancy.models import Tenant
    from apps.core_erp.tenancy.utils import get_current_tenant_id
    from .exceptions import TenantMismatchError
    if not instance.tenant_id:instance.tenant_id=get_current_tenant_id()
    if not instance.tenant_id:raise TenantMismatchError('Accounting state requires an explicit company.')
    # Provisioning can configure accounts/periods; posting separately requires ACTIVE.
    if not Tenant.objects.select_for_update().filter(pk=instance.tenant_id).exists():
        raise TenantMismatchError('Accounting company unavailable.')
    stored=type(instance).plain_objects.select_for_update().filter(pk=instance.pk).first()
    if stored and str(stored.tenant_id)!=str(instance.tenant_id):
        raise TenantMismatchError('Accounting state cannot move to another company.')
    return stored

def reject_stale(instance,stored,field,marker):
    from .exceptions import AccountingError
    previous=getattr(instance,marker,None)
    if stored and previous is not None and previous!=getattr(stored,field) and getattr(instance,field)!=getattr(stored,field):
        raise AccountingError('Accounting state changed; reload before requesting a different state.')


ACCOUNT_HASH_FIELDS={'code','type','chart_of_accounts','chart_of_accounts_id'}

def protect_account_history(instance,stored,update_fields=None):
    """A v2 journal commits account identity, but not its display label/state."""
    from .models import LedgerEntry
    from .exceptions import AccountingError
    if stored is None:return
    fields=ACCOUNT_HASH_FIELDS if update_fields is None else ACCOUNT_HASH_FIELDS & set(update_fields)
    changed=any(getattr(instance,'chart_of_accounts_id' if field=='chart_of_accounts' else field)!=getattr(stored,'chart_of_accounts_id' if field=='chart_of_accounts' else field) for field in fields)
    if changed and LedgerEntry.plain_objects.filter(account_id=stored.pk,journal_entry__is_posted=True).exists():
        raise AccountingError('Posted account identity is immutable; create a new account instead.')
