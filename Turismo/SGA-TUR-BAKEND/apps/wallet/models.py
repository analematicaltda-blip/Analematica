import uuid
import hashlib
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Wallet(models.Model):
    class OwnerType(models.TextChoices):
        AGENCIA = "AGENCIA", _("Agencia de Viajes")
        HOTEL = "HOTEL", _("Hotel / Alojamiento")
        GUIA = "GUIA", _("Guía Turístico")
        TRANSPORTE = "TRANSPORTE", _("Transporte Turístico")
        ARTESANO = "ARTESANO", _("Artesano / Productor")
        TURISTA = "TURISTA", _("Turista / Cliente Final")
        DELIVERY = "DELIVERY", _("Servicio de Delivery")
        EMPLEADO = "EMPLEADO", _("Empleado / Nómina")
        CORPORATIVO = "CORPORATIVO", _("Corporativo Interno Sarita")

    class Status(models.TextChoices):
        ACTIVO = "ACTIVO", _("Activo")
        SUSPENDIDO = "SUSPENDIDO", _("Suspendido")
        BLOQUEADO = "BLOQUEADO", _("Bloqueado por Seguridad")
        AUDITORIA = "AUDITORIA", _("En Proceso de Auditoría")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.IntegerField(null=True, blank=True, help_text="ID del CustomUser (aislamiento DB)")

    owner_type = models.CharField(max_length=20, choices=OwnerType.choices)
    owner_id = models.CharField(max_length=255, help_text="ID del perfil de negocio o usuario")

    saldo_disponible = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    saldo_bloqueado = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    saldo_en_proceso = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    estado = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVO)

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Monedero")
        verbose_name_plural = _("Monederos")
        unique_together = ('owner_type', 'owner_id')

    @property
    def user(self):
        from api.models import CustomUser
        return CustomUser.objects.filter(id=self.user_id).first()

    def __str__(self):
        return f"Wallet {self.owner_type} - {self.owner_id} ({self.saldo_disponible})"

class WalletTransaccion(models.Model):
    class Status(models.TextChoices):
        PENDIENTE = "PENDIENTE", _("Pendiente")
        PROCESANDO = "PROCESANDO", _("En Proceso")
        COMPLETADA = "COMPLETADA", _("Completada con Éxito")
        FALLIDA = "FALLIDA", _("Fallida / Rechazada")
        REVERTIDA = "REVERTIDA", _("Revertida Totalmente")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referencia_operativa = models.CharField(max_length=255, help_text="Referencia al servicio (Booking ID, Order ID, etc.)")

    monto_total = models.DecimalField(max_digits=18, decimal_places=2)
    estado = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDIENTE)

    governance_intention_id = models.CharField(max_length=255, null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def total_movimientos(self):
        return self.movimientos.aggregate(total=models.Sum('monto'))['total'] or 0

    class Meta:
        verbose_name = _("Transacción de Monedero")
        verbose_name_plural = _("Transacciones de Monedero")

class WalletMovimiento(models.Model):
    class TipoMovimiento(models.TextChoices):
        INGRESO = "INGRESO", _("Ingreso de Fondos")
        COMISION = "COMISION", _("Comisión")
        LIQUIDACION = "LIQUIDACION", _("Liquidación")
        REVERSION = "REVERSION", _("Reversión")
        RETENCION = "RETENCION", _("Retención Temporal")
        PAGO = "PAGO", _("Pago por Servicio")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='movimientos')
    transaccion = models.ForeignKey(WalletTransaccion, on_delete=models.CASCADE, related_name='movimientos')

    tipo = models.CharField(max_length=20, choices=TipoMovimiento.choices)
    monto = models.DecimalField(max_digits=18, decimal_places=2)

    referencia_modelo = models.CharField(max_length=100)
    referencia_id = models.CharField(max_length=255)

    hash_integridad = models.CharField(max_length=64, editable=False)
    creado_por_sistema = models.BooleanField(default=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.hash_integridad:
            payload = f"{self.wallet_id}{self.transaccion_id}{self.monto}{self.tipo}{self.timestamp}"
            self.hash_integridad = hashlib.sha256(payload.encode()).hexdigest()
        super().save(*args, **kwargs)

class WalletBloqueo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='bloqueos')
    transaccion = models.ForeignKey(WalletTransaccion, on_delete=models.CASCADE, null=True, blank=True)
    monto = models.DecimalField(max_digits=18, decimal_places=2)
    motivo = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)
    liberado_en = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class WalletLiquidacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=18, decimal_places=2)
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    comprobante_pago = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class WalletComision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaccion = models.ForeignKey(WalletTransaccion, on_delete=models.CASCADE, related_name='comisiones')
    receptor_wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=18, decimal_places=2)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    descripcion = models.CharField(max_length=255)

class WalletReversion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaccion_original = models.ForeignKey(WalletTransaccion, on_delete=models.PROTECT, related_name='reversiones')
    motivo = models.TextField()
    autorizado_por_id = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class WalletAuditoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    tipo_hallazgo = models.CharField(max_length=100)
    descripcion = models.TextField()
    nivel_riesgo = models.CharField(max_length=20, choices=[('BAJO', 'Bajo'), ('MEDIO', 'Medio'), ('ALTO', 'Alto'), ('CRITICO', 'Crítico')])
    resultado_esperado = models.DecimalField(max_digits=18, decimal_places=2)
    resultado_real = models.DecimalField(max_digits=18, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

class WalletLimiteOperativo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE, related_name='limite')
    monto_maximo_transaccion = models.DecimalField(max_digits=18, decimal_places=2)
    monto_maximo_diario = models.DecimalField(max_digits=18, decimal_places=2)
    requiere_aprobacion_soberana = models.BooleanField(default=False)

class WalletAlertaRiesgo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaccion = models.ForeignKey(WalletTransaccion, on_delete=models.CASCADE, null=True, blank=True)
    codigo_alerta = models.CharField(max_length=50)
    descripcion = models.TextField()
    atendida = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

# Retrocompatibilidad (Temporal para no romper servicios existentes inmediatamente)
WalletAccount = Wallet
WalletTransaction = WalletTransaccion
