from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class AssetCategory(TenantAwareModel):
    """
    Standardized to Technical English and UUID v4.
    """
    profile_id = models.UUIDField(null=True, blank=True, help_text="Decoupled reference to Operational Profile")
    name = models.CharField(max_length=150)
    useful_life_months = models.IntegerField()

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_fixed_assets'
        db_table = 'admin_fixed_assets_category'
        verbose_name = "Asset Category"

    def __str__(self):
        return self.name

class FixedAsset(TenantAwareModel):
    profile_id = models.UUIDField(null=True, blank=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='assets')
    name = models.CharField(max_length=255)
    acquisition_date = models.DateField()
    acquisition_value = models.DecimalField(max_digits=18, decimal_places=2)
    current_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_fixed_assets'
        db_table = 'admin_fixed_assets_item'
        verbose_name = "Fixed Asset"

    def __str__(self):
        return self.name

class DepreciationCalculation(TenantAwareModel):
    asset = models.ForeignKey(FixedAsset, on_delete=models.CASCADE, related_name='depreciations')
    calculation_date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    accumulated_depreciation = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_fixed_assets'
        db_table = 'admin_fixed_assets_depreciation'
        verbose_name = "Depreciation Calculation"
