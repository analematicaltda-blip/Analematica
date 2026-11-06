from django.db import models
 
from apps.core_erp.base_models import TenantAwareModel, BaseErpModel

class IntercompanyMatch(BaseErpModel):
    """
    Blueprint Alignment: Intercompany transaction matching for automatic elimination.
    """
    entity_a = models.ForeignKey('core_erp.Tenant', on_delete=models.CASCADE, related_name='matches_as_a')
    entity_b = models.ForeignKey('core_erp.Tenant', on_delete=models.CASCADE, related_name='matches_as_b')
    transaction_reference = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20, default='PENDING') # PENDING, MATCHED, ELIMINATED
    elimination_entry_id = models.UUIDField(null=True, blank=True)

    # Audit Integrity (SHA-256 Chaining)
    integrity_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    previous_hash = models.CharField(max_length=64, null=True, blank=True)

    # Metadata for full transparency
    elimination_count = models.IntegerField(default=0)
    fx_rate_set = models.JSONField(default=dict)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'core_erp'
        verbose_name = "Intercompany Match"

class ConsolidatedReportSnapshot(TenantAwareModel):
    """
    Blueprint Alignment: Multi-entity consolidated reporting snapshot.
    """
    report_name = models.CharField(max_length=255)
    period_start = models.DateField()
    period_end = models.DateField()
    consolidation_level = models.CharField(max_length=50) # HOLDING, SUB-HOLDING
    method_applied = models.CharField(max_length=20)
    data = models.JSONField() # Consolidated Trial Balance or Financial Statement
    is_certified = models.BooleanField(default=False)
    certified_by = models.CharField(max_length=100, null=True, blank=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'core_erp'
        verbose_name = "Consolidated Report Snapshot"

class IntercompanyMapping(BaseErpModel):
    """
    Formal mapping of intercompany relationships for the Holding.
    Part of the EOS Activation.
    """
    holding = models.ForeignKey('core_erp.Tenant', on_delete=models.CASCADE, related_name='ic_mappings')
    subsidiary_a = models.ForeignKey('core_erp.Tenant', on_delete=models.CASCADE, related_name='ic_mappings_as_a')
    subsidiary_b = models.ForeignKey('core_erp.Tenant', on_delete=models.CASCADE, related_name='ic_mappings_as_b')

    relationship_type = models.CharField(max_length=50) # LOAN, EQUITY, TRADING

    is_active = models.BooleanField(default=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'core_erp'
        verbose_name = "Intercompany Mapping"
 
