from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel

class DocumentoOperativo(TenantAwareModel):
    """
    Documentos vinculados a la operación diaria que deben ser trazables.
    """
    class TipoDocumento(models.TextChoices):
        CONTRATO_ADJUNTO = 'CONTRATO_ADJUNTO', 'Contrato Adjunto'
        PERMISO = 'PERMISO', 'Permiso Administrativo'
        ACTA = 'ACTA', 'Acta de Entrega'
        CERTIFICADO = 'CERTIFICADO', 'Certificado'
        OTRO = 'OTRO', 'Otro'

    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=TipoDocumento.choices, default=TipoDocumento.OTRO)
    issue_date = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    hash_archivistica = models.CharField(max_length=64, help_text="Hash SHA-256 de referencia en Gestión Archivística")

    orden_id = models.UUIDField(null=True, blank=True, help_text="Opcionalmente vinculado a una orden")

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    class Meta(TenantAwareModel.Meta):
        app_label = 'mi_negocio'
