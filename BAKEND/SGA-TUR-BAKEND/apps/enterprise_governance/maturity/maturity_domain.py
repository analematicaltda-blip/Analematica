from django.db import models
import uuid

class MaturityDomain(models.Model):
    """
    Standardized Macro-Domain for Maturity Assessment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True) # Governance, Tenancy, CRM, Finance, etc.
    description = models.TextField(blank=True)

    weight = models.FloatField(default=1.0)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'enterprise_governance'
        verbose_name = "Maturity Domain"

    def __str__(self):
        return self.name
