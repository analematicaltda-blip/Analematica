"""Reviewed liquidity classifications, additive and empty by default."""
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations,models

class Migration(migrations.Migration):
    dependencies=[('core_erp','0003_accounting_projection'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[migrations.CreateModel(name='AccountingRatioPolicy',fields=[
        ('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),
        ('created_at',models.DateTimeField(auto_now_add=True,null=True)),
        ('updated_at',models.DateTimeField(auto_now=True,null=True)),
        ('revision',models.PositiveIntegerField()),('mapping',models.JSONField()),
        ('evidence_digest',models.CharField(max_length=64)),('digest',models.CharField(max_length=64)),
        ('tenant',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to='core_erp.tenant')),
        ('reviewer',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
    ],options={'constraints':[models.UniqueConstraint(fields=('tenant','revision'),name='accounting_ratio_revision_once')]})]
