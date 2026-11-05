import uuid
from django.db import models

class SaaSPlan(models.Model):
    """
    Modelo único de Plan para el ecosistema SaaS.
    """
    class BillingType(models.TextChoices):
        FLAT = 'FLAT', 'Flat Fee'
        USAGE = 'USAGE', 'Usage Based'
        HYBRID = 'HYBRID', 'Hybrid'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    monthly_price = models.DecimalField(max_digits=12, decimal_places=2)
    annual_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Billing Logic
    billing_type = models.CharField(max_length=20, choices=BillingType.choices, default=BillingType.FLAT)
    included_usage = models.IntegerField(default=0, help_text="Units included in flat fee.")
    overage_price = models.DecimalField(max_digits=12, decimal_places=4, default=0.00)
    trial_days = models.IntegerField(default=14)

    # Resource Limits
    user_limit = models.IntegerField(default=1)
    storage_limit_gb = models.IntegerField(default=5)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class SaaSPlanVersion(models.Model):
    """
    Versioning for SaaS plans to track price changes and limit adjustments.
    """
    plan = models.ForeignKey(SaaSPlan, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    config_snapshot = models.JSONField()

    effective_from = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'commercial_engine'
        unique_together = ('plan', 'version_number')

    class Meta:
        verbose_name = "Plan SaaS"
        verbose_name_plural = "Planes SaaS"
