"""Separate local delivery acknowledgments from external publication."""
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations,models

def base_fields():
    return [('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),
            ('created_at',models.DateTimeField(auto_now_add=True,null=True)),('updated_at',models.DateTimeField(auto_now=True,null=True)),
            ('tenant',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to='core_erp.tenant'))]

class Migration(migrations.Migration):
    dependencies=[('core_erp','0002_ledger_posting_v2')]
    operations=[
        migrations.CreateModel(name='AccountingDelivery',fields=base_fields()+[
            ('event',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='accounting_deliveries',to='core_erp.outboxevent')),
            ('consumer',models.CharField(max_length=64)),('status',models.CharField(choices=[(s,s) for s in ['PENDING','LEASED','RETRY','DELIVERED','QUARANTINED']],default='PENDING',max_length=20)),
            ('payload_digest',models.CharField(blank=True,max_length=64)),('attempts',models.PositiveIntegerField(default=0)),
            ('lease_token',models.CharField(blank=True,max_length=48,null=True)),('lease_until',models.DateTimeField(blank=True,null=True)),
            ('next_attempt_at',models.DateTimeField(default=django.utils.timezone.now)),('delivered_at',models.DateTimeField(blank=True,null=True)),
            ('last_error_code',models.CharField(blank=True,default='',max_length=64)),
        ],options={'constraints':[models.UniqueConstraint(fields=('event','consumer'),name='accounting_delivery_once'),models.CheckConstraint(condition=models.Q(status__in=['PENDING','LEASED','RETRY','DELIVERED','QUARANTINED']),name='accounting_delivery_valid_status')],
                   'indexes':[models.Index(fields=['tenant','consumer','status','next_attempt_at'],name='accounting_delivery_queue')]}),
        migrations.CreateModel(name='AccountingProjectionReceipt',fields=base_fields()+[
            ('event',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to='core_erp.outboxevent')),
            ('journal',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to='core_erp.journalentry')),
            ('consumer',models.CharField(max_length=64)),('payload_digest',models.CharField(max_length=64)),('journal_hash',models.CharField(max_length=64)),
        ],options={'constraints':[models.UniqueConstraint(fields=('event','consumer'),name='accounting_projection_event_once'),models.UniqueConstraint(fields=('journal','consumer'),name='accounting_projection_journal_once')]}),
        migrations.CreateModel(name='AccountingDailyBalance',fields=base_fields()+[
            ('account',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to='core_erp.account')),
            ('economic_date',models.DateField()),('currency',models.CharField(max_length=3)),
            ('debit',models.DecimalField(decimal_places=2,default=0,max_digits=28)),('credit',models.DecimalField(decimal_places=2,default=0,max_digits=28)),
        ],options={'constraints':[models.UniqueConstraint(fields=('tenant','account','economic_date','currency'),name='accounting_daily_balance_once'),models.CheckConstraint(condition=models.Q(debit__gte=0,credit__gte=0),name='accounting_daily_nonnegative')]}),
    ]
