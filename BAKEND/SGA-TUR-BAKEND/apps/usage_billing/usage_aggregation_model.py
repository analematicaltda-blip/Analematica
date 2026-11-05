import uuid
from django.db import models
from .usage_metric_model import UsageMetric
from apps.commercial_engine.models import SaaSSubscription

class UsageAggregation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(SaaSSubscription, on_delete=models.CASCADE, related_name='usage_aggregations')
    metric = models.ForeignKey(UsageMetric, on_delete=models.PROTECT)

    period_start = models.DateField()
    period_end = models.DateField()

    total_quantity = models.DecimalField(max_digits=20, decimal_places=6, default=0)

    is_billed = models.BooleanField(default=False)
    billed_at = models.DateTimeField(null=True, blank=True)

    last_recalculated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subscription.company_id} - {self.metric.code} - {self.period_start}"

    class Meta:
        verbose_name = "Agregación de Uso"
        verbose_name_plural = "Agregaciones de Uso"
        unique_together = ('subscription', 'metric', 'period_start', 'period_end')
        app_label = 'usage_billing'
