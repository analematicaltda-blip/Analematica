"""Reviewable DML contract for core posting/reporting/local projection only.
No grants are executed. Does not cover all ERP/auth/catalog administration paths.
"""
def describe_profile():
    from django.contrib.auth import get_user_model
    from apps.core_erp.tenancy.models import Tenant
    from .models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingAuditLog,AccountingEventReceipt
    from .delivery_models import AccountingDelivery,AccountingDailyBalance,AccountingProjectionReceipt
    from .ratio_models import AccountingRatioPolicy
    from apps.core_erp.fx.models import Currency,FXRateTable
    from apps.core_erp.outbox_models import OutboxEvent
    specs=[]
    for model in (Tenant,Account,FiscalPeriod):
        specs.append({'table':model._meta.db_table,'privileges':['SELECT'],'update_columns':['id']})
    for model in (get_user_model(),ChartOfAccounts,Currency,FXRateTable):
        specs.append({'table':model._meta.db_table,'privileges':['SELECT'],'update_columns':[]})
    for model in (JournalEntry,LedgerEntry,AccountingDelivery,AccountingDailyBalance):
        specs.append({'table':model._meta.db_table,'privileges':['SELECT','INSERT','UPDATE'],'update_columns':[]})
    for model in (AccountingAuditLog,AccountingEventReceipt,AccountingProjectionReceipt,AccountingRatioPolicy):
        specs.append({'table':model._meta.db_table,'privileges':['SELECT','INSERT'],'update_columns':[]})
    specs.append({'table':OutboxEvent._meta.db_table,'privileges':['SELECT','INSERT'],'update_columns':['id']})
    return {'version':'core-accounting-dml-v1','tables':sorted(specs,key=lambda row:row['table']),
            'requires_schema_usage':True,'grants_executed':False,'production_ready':False,
            'scope':'Core posting, replay, reversal, reports and local projection; not complete ERP permissions.',
            'locking_note':'UPDATE(id) is required for SELECT FOR UPDATE; it is not tenant/account administration authorization.'}
