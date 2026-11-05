from django.contrib import admin
from .models import Horario, ExcepcionHorario

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'get_dia_semana_display', 'hora_apertura', 'hora_cierre')
    list_filter = ('perfil', 'dia_semana')
    search_fields = ('perfil__user__username',)

    def get_dia_semana_display(self, obj):
        return obj.get_dia_semana_display()
    get_dia_semana_display.short_description = 'Día de la Semana'

@admin.register(ExcepcionHorario)
class ExcepcionHorarioAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'fecha', 'esta_abierto', 'hora_apertura', 'hora_cierre', 'descripcion')
    list_filter = ('perfil', 'fecha', 'esta_abierto')
    search_fields = ('perfil__user__username', 'descripcion')
