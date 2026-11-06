from django.db import models
import uuid

class ProcessType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    class Meta:
        app_label = 'admin_archivistica'
        verbose_name = "Tipo de Proceso (Admin)"

class Process(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    process_type = models.ForeignKey(ProcessType, on_delete=models.PROTECT, related_name='admin_processes')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    class Meta:
        app_label = 'admin_archivistica'
        verbose_name = "Proceso (Admin)"

class DocumentType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    class Meta:
        app_label = 'admin_archivistica'
        verbose_name = "Tipo de Documento (Admin)"

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    process = models.ForeignKey(Process, on_delete=models.PROTECT, related_name='admin_documents')
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT, related_name='admin_documents')
    document_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'admin_archivistica'
        verbose_name = "Documento (Admin)"

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='admin_versions')
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='VERIFIED')

    class Meta:
        app_label = 'admin_archivistica'
        unique_together = ('document', 'version_number')
