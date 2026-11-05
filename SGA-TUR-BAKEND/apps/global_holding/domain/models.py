from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class JurisdictionConfig(TenantAwareModel):
    """
    Multi-country compliance and autonomy settings.
    """
    country_code = models.CharField(max_length=3, unique=True) # ISO code
    currency_code = models.CharField(max_length=3)

    autonomy_level = models.IntegerField(default=1) # 1-5
    tax_pressure_index = models.DecimalField(max_digits=5, decimal_places=4)

    is_active = models.BooleanField(default=True)
    regulatory_rules = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'global_holding'

class GlobalCapitalAllocator(TenantAwareModel):
    """
    Strategic capital distribution management.
    """
    entity_id = models.UUIDField()
    country_code = models.CharField(max_length=3)

    capital_cost = models.DecimalField(max_digits=5, decimal_places=4)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2) # 0-100

    allocation_limit = models.DecimalField(max_digits=20, decimal_places=2)
    current_allocation = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    last_rebalance = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'global_holding'

class TaxStrategy(TenantAwareModel):
    """
    Optimization of transfer pricing and global tax structure.
    """
    name = models.CharField(max_length=255)
    jurisdiction_a = models.CharField(max_length=3)
    jurisdiction_b = models.CharField(max_length=3)

    transfer_pricing_markup = models.DecimalField(max_digits=5, decimal_places=4)
    withholding_tax_rate = models.DecimalField(max_digits=5, decimal_places=4)

    is_beps_compliant = models.BooleanField(default=True)
    last_review_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'global_holding'

class TreasuryPosition(TenantAwareModel):
    """
    Global multi-currency liquidity and hedging positions.
    """
    currency = models.CharField(max_length=3)
    total_balance = models.DecimalField(max_digits=20, decimal_places=2)

    hedged_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    exposure_pct = models.DecimalField(max_digits=5, decimal_places=4)

    hedge_strategy = models.CharField(max_length=100, blank=True)

    class Meta:
        app_label = 'global_holding'

class MacroScenario(TenantAwareModel):
    """
    Geopolitical and economic structural simulations.
    """
    title = models.CharField(max_length=255)
    scenario_type = models.CharField(max_length=50) # INFLATION, WAR, REGULATORY, FX_CRASH

    impact_ebitda_pct = models.DecimalField(max_digits=5, decimal_places=4)
    impact_liquidity_pct = models.DecimalField(max_digits=5, decimal_places=4)

    probability = models.DecimalField(max_digits=5, decimal_places=4)
    is_active_sim = models.BooleanField(default=True)

    class Meta:
        app_label = 'global_holding'
