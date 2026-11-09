"""Additive ledger metadata/receipt; no rehashing or rewriting posted journals."""
import django.db.models.deletion
import uuid
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[('core_erp','0001_initial')]
    operations=[
        migrations.AddField(model_name='journalentry',name='hash_version',field=models.CharField(default='legacy',max_length=16)),
        migrations.CreateModel(name='AccountingEventReceipt',fields=[
            ('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),
            ('created_at',models.DateTimeField(auto_now_add=True,null=True)),
            ('updated_at',models.DateTimeField(auto_now=True,null=True)),
            ('event_id',models.CharField(max_length=255)),('payload_hash',models.CharField(max_length=64)),
            ('tenant',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to='core_erp.tenant')),
            ('journal',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to='core_erp.journalentry')),
        ],options={'constraints':[models.UniqueConstraint(fields=('tenant','event_id'),name='accounting_event_once_per_tenant')]}),
    ]
