from django.contrib import admin
from .models import Restaurante, Menu, CategoriaPlato, Plato, ZonaDelivery

@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil', 'ofrece_delivery')
    list_filter = ('ofrece_delivery', 'perfil')
    search_fields = ('nombre', 'perfil__user__username')

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'restaurante', 'activo')
    list_filter = ('restaurante', 'activo')
    search_fields = ('nombre', 'restaurante__nombre')

@admin.register(CategoriaPlato)
class CategoriaPlatoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'menu', 'orden')
    list_filter = ('menu__restaurante', 'menu')
    search_fields = ('nombre',)

@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'categoria', 'disponible')
    list_filter = ('categoria__menu__restaurante', 'disponible')
    search_fields = ('producto__nombre',)

@admin.register(ZonaDelivery)
class ZonaDeliveryAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'restaurante', 'costo_envio', 'tiempo_estimado_minutos')
    list_filter = ('restaurante',)
    search_fields = ('nombre', 'restaurante__nombre')
