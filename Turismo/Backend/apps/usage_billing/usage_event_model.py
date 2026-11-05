import uuid
from django.db import models
from .usage_metric_model import UsageMetric
from apps.commercial_engine.models import SaaSSubscription

class UsageEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(SaaSSubscription, on_delete=models.CASCADE, related_name='usage_events')
    metric = models.ForeignKey(UsageMetric, on_delete=models.PROTECT)

    quantity = models.DecimalField(max_digits=20, decimal_places=6)
    timestamp = models.DateTimeField(db_index=True)

    source = models.CharField(max_length=100, help_text="Origin of the event (API, AI_SERVICE, etc.)")
    metadata = models.JSONField(default=dict, blank=True)

    idempotency_key = models.CharField(max_length=100, unique=True, db_index=True)

    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subscription.company_id} - {self.metric.code}: {self.quantity}"

    class Meta:
        verbose_name = "Evento de Uso"
        verbose_name_plural = "Eventos de Uso"
        app_label = 'usage_billing'
