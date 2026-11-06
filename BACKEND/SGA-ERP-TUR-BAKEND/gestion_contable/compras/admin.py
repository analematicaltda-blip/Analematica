from django.contrib import admin
from .models import Proveedor, FacturaCompra

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'identificacion', 'telefono', 'email', 'perfil')
    search_fields = ('nombre', 'identificacion')
    list_filter = ('perfil',)

@admin.register(FacturaCompra)
class FacturaCompraAdmin(admin.ModelAdmin):
    list_display = ('number', 'proveedor', 'issue_date', 'total', 'estado', 'perfil')
    search_fields = ('number', 'proveedor__nombre')
    list_filter = ('estado', 'issue_date', 'perfil')
    date_hierarchy = 'issue_date'
