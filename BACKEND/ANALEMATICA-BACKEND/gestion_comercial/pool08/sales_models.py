"""Local opportunity metadata; no account/tenant IDs are inferred across systems."""
from django.db import models
class CommercialSale(models.Model):
    id=models.CharField(max_length=36,primary_key=True)
    scope=models.CharField(max_length=96,db_index=True)
    provider_ref=models.CharField(max_length=36,db_index=True)
    code=models.CharField(max_length=100,db_index=True)
    revision=models.PositiveIntegerField()
    status=models.CharField(max_length=20,db_index=True)
    document=models.JSONField()
    document_digest=models.CharField(max_length=64)
    class Meta:
        app_label='admin_plataforma'
        db_table='ana_commercial_sale'
class SaleEvent(models.Model):
    sequence=models.BigAutoField(primary_key=True)
    id=models.CharField(max_length=36,unique=True)
    scope=models.CharField(max_length=96,db_index=True)
    item_id=models.CharField(max_length=36,null=True,db_index=True)
    document=models.JSONField()
    class Meta:
        app_label='admin_plataforma'
        db_table='ana_commercial_sale_event'

class SaleSourceBinding(models.Model):
    id=models.UUIDField(primary_key=True,default=__import__('uuid').uuid4,editable=False)
    source_system=models.CharField(max_length=32)
    source_scope=models.CharField(max_length=96)
    source_actor=models.CharField(max_length=80)
    source_role_fingerprint=models.CharField(max_length=64)
    provider_ref=models.CharField(max_length=36)
    tenant_ref=models.CharField(max_length=36)
    actor_ref=models.CharField(max_length=80)
    reviewer_ref=models.CharField(max_length=80)
    support_digest=models.CharField(max_length=64)
    valid_until=models.DateTimeField()
    revoked_at=models.DateTimeField(null=True)
    class Meta:
        app_label='admin_plataforma'
        db_table='ana_commercial_sale_source_binding'
        constraints=[models.UniqueConstraint(fields=('source_system','source_scope','source_actor','provider_ref'),name='ana_sale_source_binding_scope')]
