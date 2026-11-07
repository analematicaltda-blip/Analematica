from django.db import models
from apps.core_erp.base_models import TenantAwareModel, BaseWarehouse, BaseInventoryMovement

class ProductCategory(TenantAwareModel):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_inventory'
        db_table = 'admin_inventory_category'
        verbose_name = "Product Category"

class Warehouse(BaseWarehouse):
    profile_id = models.UUIDField(null=True, blank=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_inventory'
        db_table = 'admin_inventory_warehouse'
        verbose_name = "Warehouse"

class Product(TenantAwareModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    current_stock = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_inventory'
        db_table = 'admin_inventory_product'
        verbose_name = "Product"

class InventoryMovement(BaseInventoryMovement):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='movements')

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_inventory'
        db_table = 'admin_inventory_movement'
        verbose_name = "Inventory Movement"
