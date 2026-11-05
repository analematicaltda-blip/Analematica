from django.contrib import admin
from .models import Empleado, Contrato, Planilla, DetalleLiquidacion, ConceptoNomina

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'identificacion', 'email', 'perfil')

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'cargo', 'salario', 'fecha_inicio', 'activo')

@admin.register(Planilla)
class PlanillaAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo_inicio', 'periodo_fin', 'estado', 'perfil')

@admin.register(DetalleLiquidacion)
class DetalleLiquidacionAdmin(admin.ModelAdmin):
    list_display = ('planilla', 'empleado', 'salario_base', 'dias_trabajados')

@admin.register(ConceptoNomina)
class ConceptoNominaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'tipo')
