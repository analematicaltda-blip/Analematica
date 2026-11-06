from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class Threshold(TenantAwareModel):
    class Operator(models.TextChoices):
        GREATER_THAN = 'GT', 'Greater Than'
        LESS_THAN = 'LT', 'Less Than'
        EQUAL = 'EQ', 'Equal'
        PCT_CHANGE_DROP = 'DROP', 'Percentage Drop'
        PCT_CHANGE_SPIKE = 'SPIKE', 'Percentage Spike'

    kpi_name = models.CharField(max_length=100)
    operator = models.CharField(max_length=10, choices=Operator.choices)
    value = models.DecimalField(max_digits=20, decimal_places=2)

    severity = models.CharField(max_length=20, default='CRITICAL')
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'control_tower'
