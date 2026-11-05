import uuid
from django.db import models

class FinancialEventRecord(models.Model):
    """
    Registro histórico de eventos que impactan CAC, LTV o ROI.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50, db_index=True)
    session_id = models.CharField(max_length=100, db_index=True) # ID de sesión de voz o lead
    value = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ['-timestamp']

class FinancialMetric(models.Model):
    """
    Snapshot de métricas calculadas por los agentes financieros.
    """
    class Meta:
        verbose_name = "Métrica Financiera"
        verbose_name_plural = "Métricas Financieras"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_name = models.CharField(max_length=20) # CAC, LTV, ROI
    dimension = models.CharField(max_length=100) # ej: 'channel:voice', 'user_type:prestador'
    value = models.FloatField()
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-calculated_at']
