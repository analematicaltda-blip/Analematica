from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class Project(TenantAwareModel):
    class Status(models.TextChoices):
        PLANNING = 'PLANNING', 'Planning'
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        ON_HOLD = 'ON_HOLD', 'On Hold'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget_allocated = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_projects'
        db_table = 'admin_project_header'
        verbose_name = "Project"

    def __str__(self):
        return self.name

class ProjectIncome(TenantAwareModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='incomes')
    date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_projects'
        db_table = 'admin_project_income'
        verbose_name = "Project Income"

class ProjectCost(TenantAwareModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='costs')
    date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Labor, Materials, Outsourcing")

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_projects'
        db_table = 'admin_project_cost'
        verbose_name = "Project Cost"
