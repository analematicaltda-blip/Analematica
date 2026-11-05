import uuid
from django.db import models

class UsageMetric(models.Model):
    class AggregationType(models.TextChoices):
        SUM = 'sum', 'Sum'
        MAX = 'max', 'Maximum'
        AVG = 'avg', 'Average'
        COUNT = 'count', 'Count'

    class PriceModel(models.TextChoices):
        FLAT = 'flat', 'Flat Fee'
        TIERED = 'tiered', 'Tiered'
        VOLUME = 'volume', 'Volume Based'
        DYNAMIC = 'dynamic', 'Dynamic'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, help_text="Ej: API_CALL, STORAGE_GB, AI_TOKEN")
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, help_text="Ej: calls, gb, tokens, users")

    aggregation_type = models.CharField(max_length=10, choices=AggregationType.choices, default=AggregationType.SUM)
    billable = models.BooleanField(default=True)
    price_model = models.CharField(max_length=10, choices=PriceModel.choices, default=PriceModel.FLAT)

    # Pricing configuration (JSON for flexibility in tiers/volume)
    pricing_config = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Métrica de Uso"
        verbose_name_plural = "Métricas de Uso"
        app_label = 'usage_billing'
