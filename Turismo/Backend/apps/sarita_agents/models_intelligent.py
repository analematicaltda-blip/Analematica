from django.db import models
import uuid

class TenienteLearning(models.Model):
    """
    Hallazgo 19: Tenientes IA con baja inteligencia.
    Permite que los Tenientes aprendan de sus ejecuciones pasadas.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teniente_id = models.CharField(max_length=255, db_index=True)
    tarea = models.TextField()
    estrategia = models.CharField(max_length=100)
    resultado = models.JSONField()
    score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Aprendizaje de Teniente"
        verbose_name_plural = "Aprendizajes de Tenientes"

class MissionHistory(models.Model):
    """
    Hallazgo 20: Coroneles no aprenden de resultados.
    Registra el historial de misiones y su scoring estratégico.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission_id = models.UUIDField(unique=True)
    mission_type = models.CharField(max_length=100, db_index=True)
    strategy = models.CharField(max_length=100)
    tenientes = models.JSONField(help_text="Lista de tenientes involucrados")
    score = models.FloatField()
    impact = models.FloatField()
    cost = models.FloatField()
    time = models.FloatField()
    result = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de Misión"
        verbose_name_plural = "Historial de Misiones"
