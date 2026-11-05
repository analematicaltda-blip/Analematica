from django.contrib import admin
from .models import TipoAlojamiento, Alojamiento, Habitacion, Tarifa

@admin.register(TipoAlojamiento)
class TipoAlojamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Alojamiento)
class AlojamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil', 'tipo', 'direccion')
    list_filter = ('tipo', 'perfil')
    search_fields = ('nombre', 'perfil__user__username')

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'alojamiento', 'capacidad_maxima')
    list_filter = ('alojamiento',)
    search_fields = ('producto__nombre', 'alojamiento__nombre')

@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'habitacion', 'fecha_inicio', 'fecha_fin', 'precio_adicional')
    list_filter = ('habitacion__alojamiento', 'fecha_inicio')
    search_fields = ('nombre', 'habitacion__producto__nombre')
