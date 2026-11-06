from django.db import models
import uuid

class MaturityMetric(models.Model):
    """
    Objective metric for a domain parameter (Model DB, Backend, etc.)
    """
    class Category(models.TextChoices):
        MODEL_DB = 'MODEL_DB', 'Database Model'
        BACKEND = 'BACKEND', 'Backend Logic'
        FRONTEND = 'FRONTEND', 'Frontend Interface'
        INTEGRATION = 'INTEGRATION', 'Cross-Domain Integration'
        AUTOMATION = 'AUTOMATION', 'Process Automation'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.ForeignKey('enterprise_governance.MaturityDomain', on_delete=models.CASCADE, related_name='metrics')

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=Category.choices)

    threshold_optimal = models.FloatField(default=100.0)
    current_value = models.FloatField(default=0.0)

    is_automated = models.BooleanField(default=True)
    validation_logic_ref = models.CharField(max_length=255, help_text="Reference to evaluator method")

    last_evaluated = models.DateTimeField(auto_now=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'enterprise_governance'
        verbose_name = "Maturity Metric"
