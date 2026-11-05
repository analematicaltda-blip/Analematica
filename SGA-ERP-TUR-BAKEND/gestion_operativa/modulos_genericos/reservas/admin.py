from django.contrib import admin
from .models import Reserva, PoliticaCancelacion, ReservaServicioAdicional

@admin.register(PoliticaCancelacion)
class PoliticaCancelacionAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'nombre', 'tipo_reembolso', 'plazo_cancelacion_horas', 'porcentaje_reembolso')
    list_filter = ('perfil', 'tipo_reembolso')
    search_fields = ('nombre', 'descripcion')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil', 'cliente', 'producto', 'estado', 'fecha_inicio', 'fecha_fin', 'costo_total')
    list_filter = ('estado', 'perfil', 'fecha_inicio')
    search_fields = ('cliente__nombre', 'producto__nombre')
    date_hierarchy = 'fecha_inicio'

@admin.register(ReservaServicioAdicional)
class ReservaServicioAdicionalAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'servicio', 'cantidad', 'precio_unitario')
    list_filter = ('reserva', 'servicio')
    search_fields = ('reserva__id', 'servicio__nombre')
