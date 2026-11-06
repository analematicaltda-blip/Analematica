from django.contrib import admin
from .models import Almacen, MovimientoInventario

@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'perfil')
    search_fields = ('name',)
    list_filter = ('perfil',)

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo_movimiento', 'quantity', 'almacen', 'date', 'usuario')
    search_fields = ('producto__nombre',)
    list_filter = ('tipo_movimiento', 'almacen', 'date')
    date_hierarchy = 'date'
