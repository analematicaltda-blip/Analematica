# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_genericos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .perfil.views import PerfilViewSet
from .clientes.views import ClienteViewSet
from .productos_servicios.views import ProductViewSet
from .inventario.views import InventoryItemViewSet
from .costos.views import CostoViewSet
from .horarios.views import HorarioViewSet, ExcepcionHorarioViewSet
from .reservas.views import ReservaViewSet, PoliticaCancelacionViewSet
from .valoraciones.views import ValoracionViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'productos-servicios', ProductViewSet, basename='producto-servicio')
router.register(r'inventario', InventoryItemViewSet, basename='inventario')
router.register(r'costos', CostoViewSet, basename='costo')
router.register(r'horarios', HorarioViewSet, basename='horario')
router.register(r'horarios-excepciones', ExcepcionHorarioViewSet, basename='horario-excepcion')
router.register(r'reservas', ReservaViewSet, basename='reserva')
router.register(r'politicas-cancelacion', PoliticaCancelacionViewSet, basename='politica-cancelacion')
router.register(r'valoraciones', ValoracionViewSet, basename='valoracion')

urlpatterns = [
    path('', include(router.urls)),

    # --- Gestión Operativa Especializada (Fase 8.5) ---
    path('esp/agencias/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.agencias.urls')),
    path('esp/agencias-de-viajes/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.agencias_de_viajes.urls')),
    path('esp/alojamientos/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.alojamientos.urls')),
    path('esp/arrendadoras-vehiculos/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.arrendadoras_vehiculos.urls')),
    path('esp/eventos/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.eventos.urls')),
    path('esp/gastronomia/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.gastronomia.urls')),
    path('esp/guias/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.guias.urls')),
    path('esp/hoteles/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.hoteles.urls')),
    path('esp/operadores-turisticos/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.operadores_turisticos.urls')),
    path('esp/restaurantes/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.restaurantes.urls')),
    path('esp/sitios-turisticos/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.sitios_turisticos.urls')),
    path('esp/transporte/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.transporte.urls')),
    path('esp/transportes/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.transportes.urls')),

]

# Redirecciones para cumplir con la paridad funcional unificada
from apps.turismo.api.urls import router as turismo_router

router.registry.extend(turismo_router.registry)
