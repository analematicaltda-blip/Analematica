from django.db import models
import uuid
from django.utils import timezone
from .modulos_genericos.perfil.models import TenantAwareModel

class ProcesoOperativo(TenantAwareModel):
    """
    Representa una orquestación de tareas para cumplir un objetivo.
    """
    class EstadoProceso(models.TextChoices):
        PLANIFICADO = 'PLANIFICADO', 'Planificado'
        EN_EJECUCION = 'EN_EJECUCION', 'En Ejecución'
        COMPLETADO = 'COMPLETADO', 'Completado'
        FALLIDO = 'FALLIDO', 'Fallido'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'

    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=EstadoProceso.choices, default=EstadoProceso.PLANIFICADO)
    inicio_real = models.DateTimeField(null=True, blank=True)
    fin_real = models.DateTimeField(null=True, blank=True)

    class Meta(TenantAwareModel.Meta):
        app_label = 'mi_negocio'

class TareaOperativa(TenantAwareModel):
    """
    Una unidad mínima de trabajo dentro de un proceso.
    """
    proceso = models.ForeignKey(ProcesoOperativo, on_delete=models.CASCADE, related_name='tareas')
    nombre = models.CharField(max_length=255)
    responsable_id = models.UUIDField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='PENDIENTE')
    fecha_limite = models.DateTimeField()

    class Meta(TenantAwareModel.Meta):
        app_label = 'mi_negocio'

class OrdenOperativa(TenantAwareModel):
    """
    Motor de ejecución derivado de un contrato.
    """
    class EstadoOrden(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PREPARACION = 'PREPARACION', 'En Preparación'
        EJECUCION = 'EJECUCION', 'En Ejecución'
        VALIDACION = 'VALIDACION', 'En Validación'
        COMPLETADA = 'COMPLETADA', 'Completada'
        INCIDENCIA = 'INCIDENCIA', 'Con Incidencia'
        CANCELADA = 'CANCELADA', 'Cancelada'

    contrato_ref_id = models.UUIDField(help_text="Referencia al Contrato Comercial")
    descripcion_servicio = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin_estimada = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=EstadoOrden.choices, default=EstadoOrden.PENDIENTE)
    responsable_lider_id = models.UUIDField(null=True, blank=True)

    costo_proyectado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_real_acumulado = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta(TenantAwareModel.Meta):
        app_label = 'mi_negocio'

class RegistroOperativo(models.Model):
    """Bitácora de transiciones y eventos de una orden."""
    orden = models.ForeignKey(OrdenOperativa, on_delete=models.CASCADE, related_name='bitacora')
    timestamp = models.DateTimeField(auto_now_add=True)
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    agente_responsable_id = models.UUIDField()
    observaciones = models.TextField(blank=True)

    class Meta:
        app_label = 'mi_negocio'

class EvidenciaOperativa(models.Model):
    """Pruebas de ejecución vinculadas a una orden."""
    orden = models.ForeignKey(OrdenOperativa, on_delete=models.CASCADE, related_name='evidencias')
    tipo = models.CharField(max_length=20, choices=[('FOTO', 'Fotografía'), ('DOC', 'Documento'), ('FIRMA', 'Firma Digital')])
    archivo_ref_id = models.UUIDField(help_text="Referencia al archivo en Gestión Archivística")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'mi_negocio'

class IncidenteOperativo(TenantAwareModel):
    """Fallas o eventos inesperados durante la ejecución."""
    orden = models.ForeignKey(OrdenOperativa, on_delete=models.CASCADE, related_name='incidencias')
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=20, choices=[('ALTA', 'Alta'), ('MEDIA', 'Media'), ('BAJA', 'Baja')], default='MEDIA')
    estado = models.CharField(max_length=20, choices=[('ABIERTA', 'Abierta'), ('EN_RESOLUCION', 'En Resolución'), ('RESUELTA', 'Resuelta')], default='ABIERTA')
    fecha_reporte = models.DateTimeField(auto_now_add=True)

    class Meta(TenantAwareModel.Meta):
        app_label = 'mi_negocio'
