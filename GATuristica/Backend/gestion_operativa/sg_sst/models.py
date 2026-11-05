from django.db import models
import uuid
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel

class MatrizRiesgo(TenantAwareModel):
    """
    Identificación de peligros, evaluación y valoración de los riesgos (IPERC).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proceso_operativo_ref_id = models.UUIDField(null=True, blank=True)
    peligro_descripcion = models.CharField(max_length=255)
    clasificacion = models.CharField(max_length=100) # Biológico, Físico, Químico, Psicosocial, etc.
    efectos_posibles = models.TextField()

    # Evaluación
    probabilidad = models.IntegerField(help_text="1 a 4")
    consecuencia = models.IntegerField(help_text="1 a 4")
    nivel_riesgo = models.IntegerField(editable=False) # probabilidad * consecuencia

    aceptabilidad = models.CharField(max_length=50) # Aceptable, No Aceptable
    criticidad = models.CharField(max_length=20, default='MEDIA') # BAJA, MEDIA, ALTA, CRITICA

    fecha_identificacion = models.DateField(auto_now_add=True)
    ultima_revision = models.DateTimeField(auto_now=True)

    version = models.IntegerField(default=1)
    es_vigente = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.nivel_riesgo = self.probabilidad * self.consecuencia
        # Lógica simple de criticidad
        if self.nivel_riesgo >= 12: self.criticidad = 'CRITICA'
        elif self.nivel_riesgo >= 8: self.criticidad = 'ALTA'
        elif self.nivel_riesgo >= 4: self.criticidad = 'MEDIA'
        else: self.criticidad = 'BAJA'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Matriz de Riesgo"
        verbose_name_plural = "Matrices de Riesgo"
        app_label = 'prestadores'

class ControlRiesgo(models.Model):
    """
    Medidas de intervención para mitigar riesgos.
    """
    matriz = models.ForeignKey(MatrizRiesgo, on_delete=models.CASCADE, related_name='controles')
    jerarquia = models.CharField(max_length=50, choices=[
        ('ELIMINACION', 'Eliminación'),
        ('SUSTITUCION', 'Sustitución'),
        ('INGENIERIA', 'Controles de Ingeniería'),
        ('ADMINISTRATIVO', 'Controles Administrativos'),
        ('EPP', 'Equipos de Protección Personal')
    ])
    descripcion_control = models.TextField()
    implementado = models.BooleanField(default=False)
    fecha_implementacion = models.DateField(null=True, blank=True)

    class Meta: app_label = 'prestadores'

class IncidenteLaboral(TenantAwareModel):
    """
    Registro detallado de accidentes e incidentes.
    """
    class TipoEvento(models.TextChoices):
        ACCIDENTE = 'ACCIDENTE', 'Accidente de Trabajo'
        INCIDENTE = 'INCIDENTE', 'Incidente (Casi accidente)'
        ENFERMEDAD = 'ENFERMEDAD', 'Enfermedad Laboral'

    class Gravedad(models.TextChoices):
        LEVE = 'LEVE', 'Leve'
        GRAVE = 'GRAVE', 'Grave'
        MORTAL = 'MORTAL', 'Mortal'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TipoEvento.choices)
    fecha_hora = models.DateTimeField()
    lugar = models.CharField(max_length=255)
    descripcion_hechos = models.TextField()
    personas_afectadas = models.JSONField(default=list) # IDs de empleados o nombres
    gravedad = models.CharField(max_length=20, choices=Gravedad.choices)

    estado_investigacion = models.CharField(max_length=50, default='PENDIENTE') # PENDING, IN_PROGRESS, CLOSED
    evidencia_archivistica_ref_id = models.UUIDField(null=True, blank=True)

    class Meta:
        verbose_name = "Incidente Laboral"
        verbose_name_plural = "Incidentes Laborales"
        app_label = 'prestadores'

class InvestigacionIncidente(models.Model):
    """
    Resultados de la investigación de un incidente.
    """
    incidente = models.OneToOneField(IncidenteLaboral, on_delete=models.CASCADE, related_name='investigacion')
    causas_basicas = models.TextField()
    causas_inmediatas = models.TextField()
    plan_accion = models.TextField()
    responsable_seguimiento_id = models.UUIDField()
    fecha_cierre = models.DateField(null=True, blank=True)

    class Meta: app_label = 'prestadores'

class PlanAnualSST(TenantAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    año = models.IntegerField()
    nombre = models.CharField(max_length=255)
    objetivo = models.TextField()
    porcentaje_cumplimiento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, default='BORRADOR') # BORRADOR, ACTIVO, CERRADO

    class Meta: app_label = 'prestadores'

class ActividadPlanSST(models.Model):
    plan = models.ForeignKey(PlanAnualSST, on_delete=models.CASCADE, related_name='actividades')
    nombre = models.CharField(max_length=255)
    fecha_programada = models.DateField()
    fecha_ejecutada = models.DateField(null=True, blank=True)
    responsable_id = models.UUIDField(null=True, blank=True)
    completada = models.BooleanField(default=False)
    evidencia_id = models.UUIDField(null=True, blank=True)

    class Meta: app_label = 'prestadores'

class InspeccionSST(TenantAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=100) # Extintores, Orden y Aseo, Botiquines, etc.
    fecha = models.DateField()
    inspector_id = models.UUIDField()
    centro_trabajo = models.CharField(max_length=255)
    porcentaje_hallazgos_cerrados = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta: app_label = 'prestadores'

class HallazgoInspeccion(models.Model):
    inspeccion = models.ForeignKey(InspeccionSST, on_delete=models.CASCADE, related_name='hallazgos')
    descripcion = models.TextField()
    criticidad = models.CharField(max_length=20, choices=[('ALTA', 'Alta'), ('MEDIA', 'Media'), ('BAJA', 'Baja')])
    plan_accion = models.TextField()
    fecha_limite = models.DateField()
    cerrado = models.BooleanField(default=False)
    fecha_cierre = models.DateField(null=True, blank=True)

    class Meta: app_label = 'prestadores'

class IndicadorSST(TenantAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=100) # Accidentalidad, Severidad, Cumplimiento Plan, etc.
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    meta = models.DecimalField(max_digits=10, decimal_places=2)
    periodo = models.CharField(max_length=50) # Enero 2024, etc.
    fecha_calculo = models.DateTimeField(auto_now_add=True)

    class Meta: app_label = 'prestadores'

class AlertaSST(TenantAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    criticidad = models.CharField(max_length=20) # CRITICA, ALTA, MEDIA, INFORMATIVA
    leida = models.BooleanField(default=False)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta: app_label = 'prestadores'

class SaludOcupacional(TenantAwareModel):
    """
    Seguimiento a la salud de los trabajadores.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado_id = models.UUIDField()
    tipo_examen = models.CharField(max_length=100) # Ingreso, Periódico, Egreso
    fecha_examen = models.DateField()
    resultado_concepto = models.CharField(max_length=100) # Apto, Apto con restricciones, No Apto
    recomendaciones = models.TextField(blank=True)
    proximo_examen = models.DateField(null=True, blank=True)

    class Meta: app_label = 'prestadores'

class CapacitacionSST(TenantAwareModel):
    """
    Registro de formación en seguridad y salud.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tema = models.CharField(max_length=255)
    fecha = models.DateField()
    intensidad_horaria = models.IntegerField()
    asistentes_count = models.IntegerField()
    evidencia_asistencia_ref_id = models.UUIDField(null=True, blank=True)
    programada = models.BooleanField(default=False)
    realizada = models.BooleanField(default=False)

    class Meta: app_label = 'prestadores'
