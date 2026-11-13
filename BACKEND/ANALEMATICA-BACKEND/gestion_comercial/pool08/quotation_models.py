"""Local opportunity metadata; no account/tenant IDs are inferred across systems."""
from django.db import models
class CommercialQuotation(models.Model):
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
        db_table='ana_commercial_quotation'
class QuotationEvent(models.Model):
    sequence=models.BigAutoField(primary_key=True)
    id=models.CharField(max_length=36,unique=True)
    scope=models.CharField(max_length=96,db_index=True)
    item_id=models.CharField(max_length=36,null=True,db_index=True)
    document=models.JSONField()
    class Meta:
        app_label='admin_plataforma'
        db_table='ana_commercial_quotation_event'

class QuotationAsset(models.Model):
    provider_ref=models.CharField(max_length=36,null=True,db_index=True)
    id=models.CharField(max_length=36,primary_key=True)
    scope=models.CharField(max_length=96,db_index=True)
    creator_ref=models.CharField(max_length=96)
    data=models.BinaryField()
    mime=models.CharField(max_length=40)
    digest=models.CharField(max_length=64)
    original_digest=models.CharField(max_length=64)
    class Meta:
        app_label='admin_plataforma'
        db_table='ana_commercial_quotation_asset'
