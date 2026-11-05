from apps.domain_business.comercial.models import (
    CommercialOperation as OperacionComercial,
    OperationItem as ItemOperacionComercial,
    SalesInvoice as FacturaVenta,
    InvoiceItem as ItemFactura
)
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel
from django.db import models

# Re-expose existing models that weren't moved yet or are specific
# (e.g. DIAN related models if they were kept there)

# Note: The original file had DianResolution, etc. I should keep them for now
# if they are not in domain_business yet.

class ReciboCaja(models.Model):
    # This might need to move too later
    perfil_ref_id = models.UUIDField()
    cuenta_bancaria_ref_id = models.UUIDField()
    factura = models.ForeignKey(FacturaVenta, on_delete=models.CASCADE, related_name='recibos_caja')
    fecha_pago = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)

class ContratoComercial(models.Model):
    operacion = models.OneToOneField(OperacionComercial, on_delete=models.CASCADE, related_name='contrato_formal')
    perfil_ref_id = models.UUIDField()
    cliente_ref_id = models.UUIDField()
    terminos_y_condiciones = models.TextField()
    fecha_firma = models.DateTimeField(null=True, blank=True)
    hash_firma_digital = models.CharField(max_length=64, null=True, blank=True)
    estado = models.CharField(max_length=20, default='BORRADOR')

class DianResolution(TenantAwareModel):
    numero_resolucion = models.CharField(max_length=100)
    prefijo = models.CharField(max_length=10)
    desde = models.PositiveIntegerField()
    hasta = models.PositiveIntegerField()
    consecutivo_actual = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    es_vigente = models.BooleanField(default=True)

    class Meta(TenantAwareModel.Meta):
        verbose_name = "Resolución DIAN"
        verbose_name_plural = "Resoluciones DIAN"

class DianCertificate(TenantAwareModel):
    nombre = models.CharField(max_length=255)
    archivo_p12 = models.FileField(upload_to='certificates/dian/')
    password_encrypted = models.CharField(max_length=512)
    fecha_vencimiento = models.DateField()
    es_activo = models.BooleanField(default=True)

class DianSoftwareConfig(TenantAwareModel):
    software_id = models.UUIDField()
    pin = models.CharField(max_length=10)
    ambiente = models.CharField(max_length=20, default='PRUEBAS')
    test_set_id = models.CharField(max_length=255, null=True, blank=True)

class DianStatusLog(models.Model):
    factura = models.ForeignKey(FacturaVenta, on_delete=models.CASCADE, related_name='dian_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    request_xml = models.TextField()
    response_xml = models.TextField()
    estado_v_previa = models.JSONField()
    success = models.BooleanField()
    error_detail = models.TextField(null=True, blank=True)
