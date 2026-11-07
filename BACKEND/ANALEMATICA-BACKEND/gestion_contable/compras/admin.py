from django.contrib import admin
from .models import Supplier, PurchaseInvoice

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id')

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'supplier', 'issue_date', 'total_amount')
