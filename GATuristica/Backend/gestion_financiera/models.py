# backend/apps/prestadores/mi_negocio/gestion_financiera/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel
# from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import ChartOfAccount
from .statements_models import *

class TesoreriaCentral(TenantAwareModel):
    """
    Entidad de gobierno central para la custodia de fondos.
    """
    saldo_total_custodia = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    reservas_totales = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    liquidez_disponible = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    ultima_conciliacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Tesorería Central"
        verbose_name_plural = "Tesorerías Centrales"

from apps.core_erp.base.base_models import BaseBankAccount

class CuentaBancaria(BaseBankAccount):
    perfil_ref_id = models.UUIDField()
    saldo_inicial = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    cuenta_contable_ref_id = models.UUIDField(null=True)

from apps.core_erp.base.base_models import BasePaymentOrder

class OrdenPago(BasePaymentOrder):
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PAGADA = 'PAGADA', 'Pagada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    perfil_ref_id = models.UUIDField()
    cuenta_bancaria_ref_id = models.UUIDField()

    # Patrón de beneficiario genérico explícito según la Directriz 14.4
    beneficiario_id = models.UUIDField(null=True, help_text="ID del beneficiario (Cliente, Proveedor, Empleado, etc.)")
    tipo_beneficiario = models.CharField(max_length=100, null=True, help_text="Tipo de beneficiario para resolución por servicio.")

    referencia_pago = models.CharField(max_length=100, blank=True)

    documento_archivistico_ref_id = models.UUIDField(null=True, blank=True)

# --- NUEVOS MODELOS FASE 6 ---

class Presupuesto(TenantAwareModel):
    nombre = models.CharField(max_length=255)
    año = models.PositiveIntegerField()
    centro_costo = models.CharField(max_length=100, blank=True, help_text="Ej: Operaciones, Marketing, Administración")
    total_estimado = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_ejecutado = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

class LineaPresupuesto(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='lineas')
    cuenta_contable_ref_id = models.UUIDField(help_text="Referencia a la cuenta de gastos/ingresos")
    nombre_item = models.CharField(max_length=255)
    monto_presupuestado = models.DecimalField(max_digits=18, decimal_places=2)
    monto_ejecutado = models.DecimalField(max_digits=18, decimal_places=2, default=0)

class CreditoFinanciero(TenantAwareModel):
    entidad_financiera = models.CharField(max_length=255)
    monto_principal = models.DecimalField(max_digits=18, decimal_places=2)
    tasa_interes_anual = models.DecimalField(max_digits=5, decimal_places=2)
    plazo_meses = models.PositiveIntegerField()
    fecha_desembolso = models.DateField()
    saldo_pendiente = models.DecimalField(max_digits=18, decimal_places=2)
    estado = models.CharField(max_length=50, default='ACTIVO') # ACTIVO, PAGADO, MORA

class CuotaCredito(models.Model):
    credito = models.ForeignKey(CreditoFinanciero, on_delete=models.CASCADE, related_name='cuotas')
    numero_cuota = models.PositiveIntegerField()
    fecha_vencimiento = models.DateField()
    monto_capital = models.DecimalField(max_digits=18, decimal_places=2)
    monto_interes = models.DecimalField(max_digits=18, decimal_places=2)
    esta_pagada = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)

class IndicadorFinancieroHistorico(TenantAwareModel):
    nombre = models.CharField(max_length=100) # Liquidez, EBITDA, etc.
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    metadata_calculo = models.JSONField(default=dict)

class AlertaFinanciera(TenantAwareModel):
    class TipoAlerta(models.TextChoices):
        DESVIACION_PRESUPUESTAL = 'DESVIACION_PRESUPUESTAL', 'Desviación Presupuestal'
        BAJA_LIQUIDEZ = 'BAJA_LIQUIDEZ', 'Baja Liquidez'
        VENCIMIENTO_CREDITO = 'VENCIMIENTO_CREDITO', 'Vencimiento de Crédito'
        INCONSISTENCIA_AUDITORIA = 'INCONSISTENCIA_AUDITORIA', 'Inconsistencia de Auditoría'

    tipo = models.CharField(max_length=50, choices=TipoAlerta.choices)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    nivel_prioridad = models.CharField(max_length=20, default='ALTA') # BAJA, MEDIA, ALTA, CRITICA
    resuelta = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

class LogFinancieroInmutable(TenantAwareModel):
    """
    Registro para auditoría forense de cambios financieros.
    """
    entidad_afectada = models.CharField(max_length=100) # Presupuesto, Credito, etc.
    registro_id = models.UUIDField()
    accion = models.CharField(max_length=100) # CREATE, UPDATE, DELETE
    datos_anteriores = models.JSONField(null=True)
    datos_nuevos = models.JSONField()
    usuario_id = models.IntegerField()
    hash_integridad = models.CharField(max_length=64, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
