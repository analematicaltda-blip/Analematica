from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class StrategicObjective(TenantAwareModel):
    title = models.CharField(max_length=255)
    description = models.TextField()

    target_value = models.DecimalField(max_digits=20, decimal_places=2)
    current_value = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    unit = models.CharField(max_length=20)

    deadline = models.DateField()
    priority = models.IntegerField(default=1) # 1: Low, 5: Critical

    is_achieved = models.BooleanField(default=False)

    class Meta:
        app_label = 'enterprise'
        verbose_name = "Strategic Objective"
