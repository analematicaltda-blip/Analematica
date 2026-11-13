"""Own durable email campaigns, audit and private results. No provider secrets stored here."""
from django.db import models
class ArmyRecord(models.Model):
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
        db_table='ana_army_job'
        constraints=[models.UniqueConstraint(fields=('scope','provider_ref','code'),name='ana_army_scope_code')]
class ArmyEvent(models.Model):
    sequence=models.BigAutoField(primary_key=True)
    id=models.CharField(max_length=36,unique=True)
    scope=models.CharField(max_length=96,db_index=True)
    item_id=models.CharField(max_length=36,null=True,db_index=True)
    document=models.JSONField()
    class Meta:
        app_label='admin_plataforma'
        db_table='ana_army_event'
