from django.contrib import admin
from .models import CompaniaTransporte, TipoVehiculo, Vehiculo, Ruta, HorarioRuta

@admin.register(CompaniaTransporte)
class CompaniaTransporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil')
    search_fields = ('nombre', 'perfil__user__username')

@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'placa', 'tipo', 'compania', 'capacidad_pasajeros')
    list_filter = ('tipo', 'compania')
    search_fields = ('producto__nombre', 'placa', 'compania__nombre')

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'compania', 'origen', 'destino')
    list_filter = ('compania',)
    search_fields = ('nombre', 'origen', 'destino')

@admin.register(HorarioRuta)
class HorarioRutaAdmin(admin.ModelAdmin):
    list_display = ('ruta', 'vehiculo', 'hora_salida', 'dias_operacion')
    list_filter = ('ruta__compania', 'vehiculo__tipo')
    search_fields = ('ruta__nombre',)
