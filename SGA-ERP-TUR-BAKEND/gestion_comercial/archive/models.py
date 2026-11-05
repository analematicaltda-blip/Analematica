from django.db import models
from django.core.files.storage import default_storage
import uuid

class CategoriaArchivo(models.Model):
    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#0070f3')

class Documento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    nombre = models.CharField(max_length=255)
    categoria = models.ForeignKey(CategoriaArchivo, on_delete=models.SET_NULL, null=True)
    archivo = models.FileField(upload_to='archive/%Y/%m/')
    version = models.CharField(max_length=20)
    tags = models.JSONField(default=list)
    full_text = models.TextField(blank=True)  # OCR
    metadata = models.JSONField(default=dict)
    prestador_ref_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

class VersionDocumento(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=20)
    archivo = models.FileField()
    changes = models.TextField()

