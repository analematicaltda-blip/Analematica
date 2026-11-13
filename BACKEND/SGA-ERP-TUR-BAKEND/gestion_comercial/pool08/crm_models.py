"""Own CRM prospects plus metadata referencing existing commercial customers."""
from django.db import models
class CRMContact(models.Model):
    id=models.CharField(max_length=96,primary_key=True)
    scope=models.CharField(max_length=96,db_index=True)
    provider_ref=models.CharField(max_length=36,db_index=True)
    customer_ref=models.PositiveBigIntegerField(null=True)
    revision=models.PositiveIntegerField()
    document=models.JSONField()
    base_fingerprint=models.CharField(max_length=64)
    class Meta:
        app_label='gestion_comercial'
        db_table='erp_commercial_crm_contact'
        constraints=[models.UniqueConstraint(fields=('scope','customer_ref'),name='erp_crm_customer_scope')]
class CRMEvent(models.Model):
    sequence=models.BigAutoField(primary_key=True)
    id=models.CharField(max_length=36,unique=True)
    scope=models.CharField(max_length=96,db_index=True)
    contact=models.CharField(max_length=96,db_index=True)
    document=models.JSONField()
    class Meta:
        app_label='gestion_comercial'
        db_table='erp_commercial_crm_event'
