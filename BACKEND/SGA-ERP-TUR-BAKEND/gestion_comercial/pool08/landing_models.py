"""Own durable landing pages; scoped identity and append-only audit."""
from django.db import models
class CommercialLanding(models.Model):
    id=models.CharField(max_length=36,primary_key=True)
    scope=models.CharField(max_length=96,db_index=True)
    provider_ref=models.CharField(max_length=36,db_index=True)
    code=models.CharField(max_length=100,db_index=True)
    revision=models.PositiveIntegerField()
    status=models.CharField(max_length=20,db_index=True)
    document=models.JSONField()
    document_digest=models.CharField(max_length=64)
    class Meta:
        app_label='gestion_comercial'
        db_table='erp_commercial_landing'
        constraints=[models.UniqueConstraint(fields=('scope','provider_ref','code'),name='erp_landing_scope_code')]
class LandingEvent(models.Model):
    sequence=models.BigAutoField(primary_key=True)
    id=models.CharField(max_length=36,unique=True)
    scope=models.CharField(max_length=96,db_index=True)
    item_id=models.CharField(max_length=36,null=True,db_index=True)
    document=models.JSONField()
    class Meta:
        app_label='gestion_comercial'
        db_table='erp_commercial_landing_event'

