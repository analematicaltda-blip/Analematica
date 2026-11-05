from django.db import models
from django.conf import settings
import uuid
from decimal import Decimal

class FacturaElectronica(models.Model):
    CUFE_LENGTH = 188  # DIAN standard

    class EstadoDIAN(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        ACEPTADA = 'aceptada', 'Aceptada'
        RECHAZADA = 'rechazada', 'Rechazada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operacion_comercial = models.OneToOneField('domain_business.CommercialOperation', on_delete=models.CASCADE, related_name='factura_electronica')
    cufe = models.CharField(max_length=CUFE_LENGTH, unique=True)
    xml_content = models.TextField()  # Base64 XML DIAN
    pdf_url = models.URLField(blank=True)
    estado_dian = models.CharField(max_length=20, choices=EstadoDIAN.choices, default=EstadoDIAN.PENDIENTE)
    codigo_respuesta_dian = models.CharField(max_length=20)
    fecha_envio_dian = models.DateTimeField(null=True, blank=True)
    fecha_respuesta_dian = models.DateTimeField(null=True, blank=True)
    email_enviada = models.BooleanField(default=False)
    prestador_email = models.EmailField()  # From profile
    tenant_id = models.CharField(max_length=36)

    def __str__(self):
        return f'Factura {self.cufe[:20]}... ({self.estado_dian})'

