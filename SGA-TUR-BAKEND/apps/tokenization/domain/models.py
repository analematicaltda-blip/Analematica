from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class TokenizedAsset(TenantAwareModel):
    """
    Base model for programmable digital assets.
    """
    class AssetType(models.TextChoices):
        EQUITY = 'EQUITY', 'Equity Token'
        DEBT = 'DEBT', 'Debt Token'
        REVENUE_SHARE = 'REVENUE_SHARE', 'Revenue Share Token'
        ASSET_BACKED = 'ASSET_BACKED', 'Asset-Backed Token'
        IP = 'IP', 'IP Token'
        INFRASTRUCTURE = 'INFRASTRUCTURE', 'Infrastructure Token'

    class RegulatoryClassification(models.TextChoices):
        SECURITY = 'SECURITY', 'Security Token'
        UTILITY = 'UTILITY', 'Utility Token'
        HYBRID = 'HYBRID', 'Hybrid Instrument'

    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=50, choices=AssetType.choices)
    classification = models.CharField(max_length=50, choices=RegulatoryClassification.choices)

    underlying_asset_ref_id = models.UUIDField(null=True, blank=True, help_text="Reference to physical/ledger asset")
    valuation_model = models.CharField(max_length=100, help_text="Method used for valuation (e.g. DCF, NAV)")

    jurisdiction = models.CharField(max_length=3, help_text="ISO Country Code")
    total_supply = models.DecimalField(max_digits=30, decimal_places=10)
    par_value = models.DecimalField(max_digits=20, decimal_places=2)

    governance_rules = models.JSONField(default=dict, blank=True)
    transfer_constraints = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'tokenization'

class ProgrammableCapitalUnit(TenantAwareModel):
    """
    Units representing portions of the holding or specific projects.
    """
    asset = models.ForeignKey(TokenizedAsset, on_delete=models.CASCADE, related_name='units')
    unit_id = models.CharField(max_length=100, unique=True)

    ownership_percentage = models.DecimalField(max_digits=10, decimal_places=8)
    current_holder_id = models.UUIDField(db_index=True) # Reference to Investor/Entity

    automated_distribution_rules = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'tokenization'

class SmartGovernanceRule(TenantAwareModel):
    """
    Rules for automated corporate actions on tokenized assets.
    """
    asset = models.ForeignKey(TokenizedAsset, on_delete=models.CASCADE, related_name='rules')
    trigger_event = models.CharField(max_length=100) # e.g. DIVIDEND_DECLARED, INTEREST_DUE

    logic_code = models.TextField(help_text="DSL or Python snippet for automated execution")
    autonomy_level = models.IntegerField(default=1) # 1-5

    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'tokenization'

class DigitalRegistry(TenantAwareModel):
    """
    Inmutable record of token ownership and transfers.
    """
    asset = models.ForeignKey(TokenizedAsset, on_delete=models.CASCADE)
    unit = models.ForeignKey(ProgrammableCapitalUnit, on_delete=models.SET_NULL, null=True, blank=True)

    from_holder_id = models.UUIDField(null=True, blank=True)
    to_holder_id = models.UUIDField()

    quantity = models.DecimalField(max_digits=30, decimal_places=10)
    transaction_hash = models.CharField(max_length=64, unique=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'tokenization'
        ordering = ['-timestamp']

class ComplianceConstraint(TenantAwareModel):
    """
    Jurisdiction-specific regulatory rules for token transfers.
    """
    jurisdiction = models.CharField(max_length=3)
    rule_type = models.CharField(max_length=50) # e.g. KYC, AML, LOCKUP, MAX_INVESTORS

    parameters = models.JSONField()
    is_blocking = models.BooleanField(default=True)

    class Meta:
        app_label = 'tokenization'
