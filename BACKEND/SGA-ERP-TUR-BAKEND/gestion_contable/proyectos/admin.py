from django.contrib import admin
from .models import Proyecto, IngresoProyecto, CostoProyecto

class IngresoProyectoInline(admin.TabularInline):
    model = IngresoProyecto
    extra = 1

class CostoProyectoInline(admin.TabularInline):
    model = CostoProyecto
    extra = 1

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'estado', 'presupuesto', 'perfil')
    search_fields = ('nombre',)
    list_filter = ('estado', 'perfil')
    inlines = [IngresoProyectoInline, CostoProyectoInline]

@admin.register(IngresoProyecto)
class IngresoProyectoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'descripcion', 'monto', 'fecha')
    search_fields = ('proyecto__nombre', 'descripcion')

@admin.register(CostoProyecto)
class CostoProyectoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'descripcion', 'monto', 'fecha')
    search_fields = ('proyecto__nombre', 'descripcion')
