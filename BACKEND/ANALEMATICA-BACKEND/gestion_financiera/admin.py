from django.contrib import admin
from .models import CuentaBancaria, TransaccionBancaria, OrdenPago

@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_number', 'balance')

@admin.register(TransaccionBancaria)
class TransaccionBancariaAdmin(admin.ModelAdmin):
    list_display = ('cuenta', 'amount', 'payment_date')

@admin.register(OrdenPago)
class OrdenPagoAdmin(admin.ModelAdmin):
    list_display = ('concept', 'amount', 'status', 'payment_date')
