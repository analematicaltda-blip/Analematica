from django.db import models
import uuid

# Se asume que los modelos CustomUser y Company ya existen en otras apps.
# Usamos strings 'api.CustomUser' y 'companies.Company' para evitar importaciones circulares.

class ProcessType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='archivistica_process_types')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'gestion_archivistica'

class Process(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='archivistica_processes')
    process_type = models.ForeignKey(ProcessType, on_delete=models.PROTECT, related_name='processes')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'gestion_archivistica'

class DocumentType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='archivistica_document_types')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'gestion_archivistica'

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='archivistica_documents')
    process = models.ForeignKey(Process, on_delete=models.PROTECT)
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    sequence = models.PositiveIntegerField()
    document_code = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey('api.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'process', 'document_type', 'sequence')
        app_label = 'gestion_archivistica'

    def __str__(self):
        return self.document_code

class DocumentVersion(models.Model):
    class ProcessingStatus(models.TextChoices):
        PENDING_UPLOAD = 'PENDING_UPLOAD', 'Pendiente de Subida'
        PENDING_CONFIRMATION = 'PENDING_CONFIRMATION', 'Pendiente de Confirmación'
        IN_BATCH = 'IN_BATCH', 'En Lote para Notarización'
        VERIFIED = 'VERIFIED', 'Verificado'
        COMPROMISED = 'COMPROMISED', 'Comprometido'

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    validity_year = models.IntegerField()
    uploaded_by = models.ForeignKey('api.CustomUser', on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=ProcessingStatus.choices, default=ProcessingStatus.PENDING_UPLOAD)

    # Campos que se llenan asíncronamente
    external_file_id = models.CharField(max_length=1024, null=True, blank=True) # ID en S3/Drive
    file_hash_sha256 = models.CharField(max_length=64, null=True, blank=True)

    # Campos de prueba de Blockchain
    merkle_root = models.CharField(max_length=66, null=True, blank=True)
    merkle_proof = models.JSONField(null=True, blank=True)
    blockchain_transaction = models.CharField(max_length=66, null=True, blank=True)
    blockchain_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('document', 'version_number')
        ordering = ['-version_number']
        app_label = 'gestion_archivistica'

    def __str__(self):
        return f"{self.document.document_code} - v{self.version_number}"
