"""Own durable landing pages; scoped identity and append-only audit."""
from django.db import models
class LibraryItem(models.Model):
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
        db_table='ana_media_library'
        constraints=[models.UniqueConstraint(fields=('scope','provider_ref','code'),name='ana_library_scope_code')]
class LibraryEvent(models.Model):
    sequence=models.BigAutoField(primary_key=True)
    id=models.CharField(max_length=36,unique=True)
    scope=models.CharField(max_length=96,db_index=True)
    item_id=models.CharField(max_length=36,null=True,db_index=True)
    document=models.JSONField()
    class Meta:
        app_label='admin_plataforma'
        db_table='ana_media_library_event'


class LibraryBlob(models.Model):
    id=models.CharField(max_length=36,primary_key=True)
    scope=models.CharField(max_length=96,db_index=True)
    provider_ref=models.CharField(max_length=36,db_index=True)
    original=models.BinaryField()
    delivery=models.BinaryField()
    original_sha=models.CharField(max_length=64)
    delivery_sha=models.CharField(max_length=64)
    mime=models.CharField(max_length=40)
    class Meta:
        app_label='admin_plataforma'
        db_table='ana_media_library_blob'
