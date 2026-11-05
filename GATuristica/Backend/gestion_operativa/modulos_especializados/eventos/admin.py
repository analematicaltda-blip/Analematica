from django.contrib import admin
from .models import OrganizadorEvento, Evento, Promocion

@admin.register(OrganizadorEvento)
class OrganizadorEventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil')
    search_fields = ('nombre', 'perfil__user__username')

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'organizador', 'fecha_inicio', 'fecha_fin', 'ubicacion')
    list_filter = ('organizador', 'fecha_inicio')
    search_fields = ('producto__nombre', 'organizador__nombre')

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil', 'tipo_descuento', 'valor_descuento', 'fecha_inicio', 'fecha_fin', 'activa')
    list_filter = ('perfil', 'tipo_descuento', 'activa')
    search_fields = ('nombre', 'descripcion')
    filter_horizontal = ('productos_aplicables',)

    def get_queryset(self, request):
        # Optimiza la carga de productos_aplicables
        return super().get_queryset(request).prefetch_related('productos_aplicables')
