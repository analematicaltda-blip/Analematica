from django.contrib import admin
from .models import Valoracion

@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('producto', 'turista', 'puntuacion', 'fecha_creacion', 'perfil_prestador')
    list_filter = ('puntuacion', 'fecha_creacion', 'perfil_prestador')
    search_fields = ('producto__nombre', 'turista__username', 'comentario')
    readonly_fields = ('fecha_creacion', 'fecha_respuesta')
    fieldsets = (
        (None, {
            'fields': ('producto', 'turista', 'puntuacion', 'comentario', 'fecha_creacion')
        }),
        ('Respuesta del Prestador', {
            'fields': ('respuesta_del_prestador', 'fecha_respuesta')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('producto', 'turista', 'perfil_prestador')
