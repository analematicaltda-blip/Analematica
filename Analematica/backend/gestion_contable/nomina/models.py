from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class Employee(TenantAwareModel):
    """
    Represents an employee in the Holding/Tenant context.
    Standardized to Technical English and UUID v4.
    """
    profile_id = models.UUIDField(null=True, blank=True, help_text="Decoupled reference to Operational Profile")
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    tax_id = models.CharField(max_length=50, unique=True, help_text="SSN or National ID")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_payroll'
        db_table = 'admin_payroll_employee'
        verbose_name = "Employee"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class EmploymentContract(TenantAwareModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contracts')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    base_salary = models.DecimalField(max_digits=18, decimal_places=2)
    position = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_payroll'
        db_table = 'admin_payroll_contract'
        verbose_name = "Employment Contract"

class PayrollConcept(TenantAwareModel):
    class Type(models.TextChoices):
        EARNING = 'EARNING', 'Earning'
        DEDUCTION = 'DEDUCTION', 'Deduction'

    code = models.CharField(max_length=20, unique=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.EARNING)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_payroll'
        db_table = 'admin_payroll_concept'
        verbose_name = "Payroll Concept"

class PayrollRun(TenantAwareModel):
    """
    Previously 'Planilla'. Represents a payroll execution for a period.
    """
    profile_id = models.UUIDField(null=True, blank=True)
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    month = models.IntegerField()
    year = models.IntegerField()
    total_earnings = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    total_deductions = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    net_total = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_payroll'
        db_table = 'admin_payroll_run'
        verbose_name = "Payroll Run"

class PayrollNews(TenantAwareModel):
    """
    Previously 'NovedadNomina'.
    """
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='news', null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_news')
    concept = models.ForeignKey(PayrollConcept, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_payroll'
        db_table = 'admin_payroll_news'
        verbose_name = "Payroll News"

class PayrollDetail(TenantAwareModel):
    """
    Previously 'DetalleLiquidacion'.
    """
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='details')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    total_earnings = models.DecimalField(max_digits=18, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=18, decimal_places=2)
    net_pay = models.DecimalField(max_digits=18, decimal_places=2)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_payroll'
        db_table = 'admin_payroll_detail'
        verbose_name = "Payroll Detail"
