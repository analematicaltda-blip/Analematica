"""Durable local delivery state, consumer receipts and rebuildable projections."""
from django.db import models
from django.utils import timezone
from apps.core_erp.base_models import BaseErpModel

class AccountingDelivery(BaseErpModel):
    tenant=models.ForeignKey('core_erp.Tenant',on_delete=models.PROTECT)
    event=models.ForeignKey('core_erp.OutboxEvent',on_delete=models.PROTECT,related_name='accounting_deliveries')
    consumer=models.CharField(max_length=64)
    status=models.CharField(max_length=20,default='PENDING',choices=[(s,s) for s in ['PENDING','LEASED','RETRY','DELIVERED','QUARANTINED']])
    payload_digest=models.CharField(max_length=64,blank=True)
    attempts=models.PositiveIntegerField(default=0)
    lease_token=models.CharField(max_length=48,null=True,blank=True)
    lease_until=models.DateTimeField(null=True,blank=True)
    next_attempt_at=models.DateTimeField(default=timezone.now)
    delivered_at=models.DateTimeField(null=True,blank=True)
    last_error_code=models.CharField(max_length=64,blank=True,default='')
    class Meta:
        app_label='core_erp'
        constraints=[models.UniqueConstraint(fields=['event','consumer'],name='accounting_delivery_once'),
                     models.CheckConstraint(condition=models.Q(status__in=['PENDING','LEASED','RETRY','DELIVERED','QUARANTINED']),name='accounting_delivery_valid_status')]
        indexes=[models.Index(fields=['tenant','consumer','status','next_attempt_at'],name='accounting_delivery_queue')]

class AccountingProjectionReceipt(BaseErpModel):
    tenant=models.ForeignKey('core_erp.Tenant',on_delete=models.PROTECT)
    event=models.ForeignKey('core_erp.OutboxEvent',on_delete=models.PROTECT)
    journal=models.ForeignKey('core_erp.JournalEntry',on_delete=models.PROTECT)
    consumer=models.CharField(max_length=64)
    payload_digest=models.CharField(max_length=64)
    journal_hash=models.CharField(max_length=64)
    class Meta:
        app_label='core_erp'
        constraints=[models.UniqueConstraint(fields=['event','consumer'],name='accounting_projection_event_once'),
                     models.UniqueConstraint(fields=['journal','consumer'],name='accounting_projection_journal_once')]

class AccountingDailyBalance(BaseErpModel):
    tenant=models.ForeignKey('core_erp.Tenant',on_delete=models.PROTECT)
    account=models.ForeignKey('core_erp.Account',on_delete=models.PROTECT)
    economic_date=models.DateField()
    currency=models.CharField(max_length=3)
    debit=models.DecimalField(max_digits=28,decimal_places=2,default=0)
    credit=models.DecimalField(max_digits=28,decimal_places=2,default=0)
    class Meta:
        app_label='core_erp'
        constraints=[models.UniqueConstraint(fields=['tenant','account','economic_date','currency'],name='accounting_daily_balance_once'),
                     models.CheckConstraint(condition=models.Q(debit__gte=0,credit__gte=0),name='accounting_daily_nonnegative')]
