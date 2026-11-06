from django.db import models
import uuid
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel

class EstadoResultados(TenantAwareModel):
    """
    Representa el Estado de Resultados (P&L) para un periodo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periodo_contable_ref_id = models.UUIDField()
    ingresos_totales = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    costos_totales = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    gastos_totales = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    utilidad_neta = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    metadata_detalle = models.JSONField(default=dict) # Desglose por cuentas
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estado de Resultados"
        verbose_name_plural = "Estados de Resultados"

class BalanceGeneral(TenantAwareModel):
    """
    Representa el Balance General (Estado de Situación Financiera).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha_corte = models.DateField()
    total_activos = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_pasivos = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_patrimonio = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    metadata_detalle = models.JSONField(default=dict)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

class FlujoEfectivo(TenantAwareModel):
    """
    Estado de Flujos de Efectivo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periodo_contable_ref_id = models.UUIDField()
    actividades_operacion = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    actividades_inversion = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    actividades_financiacion = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    efectivo_final = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    metadata_detalle = models.JSONField(default=dict)

class CambiosPatrimonio(TenantAwareModel):
    """
    Estado de Cambios en el Patrimonio.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periodo_contable_ref_id = models.UUIDField()
    saldo_inicial = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    aumentos = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    disminuciones = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    metadata_detalle = models.JSONField(default=dict)

class ReservaFinanciera(TenantAwareModel):
    """
    Reservas obligatorias o estatutarias.
    """
    nombre = models.CharField(max_length=255)
    monto_objetivo = models.DecimalField(max_digits=18, decimal_places=2)
    monto_actual = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    proposito = models.TextField()

class ProyeccionFinanciera(TenantAwareModel):
    """
    Escenarios y proyecciones de ingresos/gastos.
    """
    nombre_escenario = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    ingresos_proyectados = models.DecimalField(max_digits=18, decimal_places=2)
    gastos_proyectados = models.DecimalField(max_digits=18, decimal_places=2)
    nivel_probabilidad = models.FloatField(help_text="0.0 a 1.0")

class RiesgoFinanciero(TenantAwareModel):
    """
    Registro de riesgos identificados por el sistema.
    """
    class NivelRiesgo(models.TextChoices):
        BAJO = 'BAJO', 'Bajo'
        MEDIO = 'MEDIO', 'Medio'
        ALTO = 'ALTO', 'Alto'
        CRITICO = 'CRITICO', 'Crítico'

    tipo_riesgo = models.CharField(max_length=100) # Liquidez, Mercado, Crédito
    descripcion = models.TextField()
    impacto_estimado = models.DecimalField(max_digits=18, decimal_places=2)
    nivel = models.CharField(max_length=20, choices=NivelRiesgo.choices)
    mitigacion_sugerida = models.TextField()
    activo = models.BooleanField(default=True)
