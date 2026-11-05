from django.db import models
from apps.core_erp.base_models import TenantAwareModel, LedgerAccount

class Budget(TenantAwareModel):
    name = models.CharField(max_length=200)
    fiscal_year = models.IntegerField()
    total_estimated_income = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    total_estimated_expenses = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_budget'
        db_table = 'admin_budget_header'
        verbose_name = "Budget"

class BudgetItem(TenantAwareModel):
    class Type(models.TextChoices):
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'

    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    # Using the Proxy or Core Account if needed
    account_code = models.CharField(max_length=20)
    type = models.CharField(max_length=20, choices=Type.choices)
    estimated_amount = models.DecimalField(max_digits=18, decimal_places=2)
    executed_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_budget'
        db_table = 'admin_budget_item'
        verbose_name = "Budget Item"

class BudgetExecution(TenantAwareModel):
    item = models.ForeignKey(BudgetItem, on_delete=models.CASCADE, related_name='executions')
    date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    reference_id = models.UUIDField(null=True, blank=True, help_text="Reference to the transaction that triggered this execution")

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_budget'
        db_table = 'admin_budget_execution'
        verbose_name = "Budget Execution"
