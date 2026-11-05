from django.contrib import admin
from .models import OperadorTuristico, PaqueteTuristico, ItinerarioDia

class ItinerarioDiaInline(admin.TabularInline):
    model = ItinerarioDia
    extra = 1

@admin.register(OperadorTuristico)
class OperadorTuristicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil', 'licencia_turismo')
    search_fields = ('nombre', 'perfil__user__username')

@admin.register(PaqueteTuristico)
class PaqueteTuristicoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'operador', 'duracion_dias')
    list_filter = ('operador',)
    search_fields = ('producto__nombre', 'operador__nombre')
    inlines = [ItinerarioDiaInline]

@admin.register(ItinerarioDia)
class ItinerarioDiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'paquete', 'dia')
    list_filter = ('paquete__operador',)
    search_fields = ('titulo', 'paquete__producto__nombre')
