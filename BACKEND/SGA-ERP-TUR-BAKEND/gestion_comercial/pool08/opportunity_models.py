"""Local opportunity metadata; no account/tenant IDs are inferred across systems."""
from django.db import models
class CommercialOpportunity(models.Model):
    id=models.CharField(max_length=36,primary_key=True)
    scope=models.CharField(max_length=96,db_index=True)
    provider_ref=models.CharField(max_length=36,db_index=True)
    legacy_ref=models.UUIDField(null=True)
    revision=models.PositiveIntegerField()
    stage=models.CharField(max_length=20,db_index=True)
    document=models.JSONField()
    document_digest=models.CharField(max_length=64)
    base_fingerprint=models.CharField(max_length=64)
    class Meta:
        app_label='gestion_comercial'
        db_table='erp_commercial_opportunity'
        constraints=[models.UniqueConstraint(fields=('scope','legacy_ref'),name='erp_opportunity_legacy_scope')]
class OpportunityEvent(models.Model):
    sequence=models.BigAutoField(primary_key=True)
    id=models.CharField(max_length=36,unique=True)
    scope=models.CharField(max_length=96,db_index=True)
    opportunity=models.CharField(max_length=36,db_index=True)
    document=models.JSONField()
    class Meta:
        app_label='gestion_comercial'
        db_table='erp_commercial_opportunity_event'
