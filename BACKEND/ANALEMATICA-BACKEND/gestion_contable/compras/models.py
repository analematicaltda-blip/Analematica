from django.db import models
from apps.core_erp.base_models import TenantAwareModel, BaseInvoice

class Supplier(TenantAwareModel):
    """
    Standardized to Technical English and UUID v4.
    """
    profile_id = models.UUIDField(null=True, blank=True, help_text="Decoupled reference to Operational Profile")
    name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_procurement'
        db_table = 'admin_procurement_supplier'
        verbose_name = "Supplier"

    def __str__(self):
        return self.name

class PurchaseInvoice(BaseInvoice): # Inherits from BaseInvoice which is already TenantAware
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='invoices')
    description = models.TextField(blank=True, null=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_procurement'
        db_table = 'admin_procurement_invoice'
        verbose_name = "Purchase Invoice"
