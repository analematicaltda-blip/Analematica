# backend/apps/sarita_agents/models.py
import uuid
from django.db import models

# --- MODELOS DE INTELIGENCIA ---
from .models_intelligent import TenienteLearning, MissionHistory

class Mision(models.Model):
    """
    Registro de más alto nivel. Representa la directiva original del General.

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idempotency_key = models.UUIDField(unique=True, null=True, blank=True, help_text="Clave única para prevenir duplicados.")

    directiva_original = models.JSONField(help_text="La directiva JSON original recibida por el orquestador.")
    dominio = models.CharField(max_length=100, db_index=True, help_text="Dominio de negocio objetivo (ej. 'prestadores').")
    estado = models.CharField(max_length=50, default='PENDIENTE', db_index=True, choices=[
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADA', 'Completada'),
        ('FALLIDA', 'Fallida'),

        ('COMPLETADA_PARCIALMENTE', 'Completada Parcialmente'),

    ])
    resultado_final = models.JSONField(null=True, blank=True, help_text="El informe final consolidado de la misión.")
    timestamp_inicio = models.DateTimeField(auto_now_add=True)
    timestamp_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Misión {self.id} ({self.dominio}) - {self.estado}"

class PlanTáctico(models.Model):
    """
    El plan detallado generado por un Capitán para cumplir una misión.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mision = models.ForeignKey(Mision, on_delete=models.CASCADE, related_name='planes_tacticos')
    capitan_responsable = models.CharField(max_length=255, db_index=True, help_text="Clase del Capitán que generó el plan.")
    pasos_del_plan = models.JSONField(help_text="Los pasos estructurados del plan.")
    estado = models.CharField(max_length=50, default='PLANIFICADO', db_index=True, choices=[
        ('PLANIFICADO', 'Planificado'),
        ('EN_EJECUCION', 'En Ejecución'),
        ('COMPLETADO', 'Completado'),
        ('FALLIDO', 'Fallido'),

        ('COMPLETADO_PARCIALMENTE', 'Completado Parcialmente'),

    ])
    timestamp_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan {self.id} para Misión {self.mision_id}"

class TareaDelegada(models.Model):
    """
    Una tarea atómica individual delegada a un Teniente.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_tactico = models.ForeignKey(PlanTáctico, on_delete=models.CASCADE, related_name='tareas')
    teniente_asignado = models.CharField(max_length=255, db_index=True, help_text="Identificador del Teniente responsable.")
    descripcion_tarea = models.TextField()
    parametros = models.JSONField(default=dict)
    estado = models.CharField(max_length=50, default='PENDIENTE', db_index=True, choices=[
        ('PENDIENTE', 'Pendiente'),

        ('EN_COLA', 'En Cola'),
        ('EN_PROGRESO', 'En Progreso'),
        ('REINTENTANDO', 'Reintentando'),

        ('COMPLETADA', 'Completada'),
        ('FALLIDA', 'Fallida'),
    ])
    timestamp_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tarea {self.id} ({self.estado})"

class RegistroDeEjecucion(models.Model):
    """
    Un log detallado de un intento de ejecución de una TareaDelegada.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tarea_delegada = models.ForeignKey(TareaDelegada, on_delete=models.CASCADE, related_name='logs_ejecucion')
    timestamp = models.DateTimeField(auto_now_add=True)
    exitoso = models.BooleanField()
    salida_log = models.TextField(null=True, blank=True, help_text="Salida estándar o log de la ejecución.")
    resultado = models.JSONField(null=True, blank=True, help_text="El resultado estructurado de la ejecución.")

    def __str__(self):
        return f"Log de Tarea {self.tarea_delegada_id} @ {self.timestamp}"

class MicroTarea(models.Model):
    """
    NIVEL 6: Ejecutada por un Soldado bajo la supervisión de un Sargento.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tarea_padre = models.ForeignKey(TareaDelegada, on_delete=models.CASCADE, related_name='micro_tareas')
    soldado_asignado = models.CharField(max_length=255, db_index=True)
    descripcion = models.TextField()
    parametros = models.JSONField(default=dict)
    estado = models.CharField(max_length=50, default='PENDIENTE', db_index=True, choices=[
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADA', 'Completada'),
        ('FALLIDA', 'Fallida'),
    ])
    timestamp_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MicroTarea {self.id} ({self.estado}) - {self.soldado_asignado}"

class RegistroMicroTarea(models.Model):
    """
    Log de ejecución detallado para un Soldado.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    micro_tarea = models.ForeignKey(MicroTarea, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    exitoso = models.BooleanField(db_index=True)
    resultado = models.JSONField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

# --- Modelos de Dominio (Ejemplo para Fase U) ---

class Prestador(models.Model):
    """
    Modelo simple para representar a un Prestador de Servicios Turísticos.
    Creado para la prueba de concepto de la Fase U.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    activo = models.BooleanField(default=False)
    timestamp_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.email})"

class IdempotencyKey(models.Model):
    key = models.CharField(max_length=255, db_index=True)
    domain = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, default='PENDING') # PENDING, SUCCESS, FAILED
    response_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('key', 'domain')

class SoldadoOperationalStatus(models.Model):
    nombre_soldado = models.CharField(max_length=255, primary_key=True)
    dominio = models.CharField(max_length=100, db_index=True)
    estado = models.CharField(max_length=50, default='Mock') # Mock, Operacional, Certificado
    fecha_certificacion = models.DateTimeField(null=True, blank=True)
