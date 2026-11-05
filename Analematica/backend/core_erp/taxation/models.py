from django.db import models
from apps.core_erp.base_models import BaseErpModel, TenantAwareModel

class Country(BaseErpModel):
    """Bloque 3.1: Tabla de Países"""
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=10, unique=True)
    currency_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.iso_code})"

class Jurisdiction(BaseErpModel):
    """Bloque 3.2: Tabla de Jurisdicciones"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='jurisdictions')
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=50, choices=[('NATIONAL', 'National'), ('REGIONAL', 'Regional'), ('MUNICIPAL', 'Municipal')])

    def __str__(self):
        return f"{self.name} - {self.level}"

class Tax(TenantAwareModel):
    """Bloque 3.3: Tabla de Impuestos"""
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=150)
    tax_type = models.CharField(max_length=50) # IVA, RET, ISR, ICA
    jurisdiction = models.ForeignKey(Jurisdiction, on_delete=models.CASCADE, related_name='taxes')
    deductible = models.BooleanField(default=False)
    withholding = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('code', 'tenant')

class TaxRate(BaseErpModel):
    """Bloque 3.4: Tabla de Tasas"""
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, related_name='rates')
    rate = models.DecimalField(max_digits=10, decimal_places=6)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

class TaxRule(BaseErpModel):
    """Bloque 3.5: Tabla de Reglas"""
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, related_name='rules')
    document_type = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50)
    minimum_base = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    maximum_base = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    condition_expression = models.TextField(blank=True)
    priority = models.IntegerField(default=0)

class TaxTransaction(TenantAwareModel):
    """Bloque 3.6: Tabla de Transacciones Fiscales"""
    document_id = models.UUIDField(db_index=True)
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT)
    base_amount = models.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2)
    rate_applied = models.DecimalField(max_digits=10, decimal_places=6)

    # Audit Integrity (Fase Z)
    integrity_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)

class TaxAccountMapping(TenantAwareModel):
    """Bloque 3.7: Mapeo Contable"""
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, related_name='account_mappings')
    debit_account = models.CharField(max_length=50)
    credit_account = models.CharField(max_length=50)
