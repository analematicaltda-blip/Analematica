# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/sitios_turisticos/views.py
from rest_framework import viewsets, permissions
from .models import SitioTuristico, ActividadEnSitio
from .serializers import SitioTuristicoSerializer, ActividadEnSitioSerializer
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.permissions import IsOwner

class SitioTuristicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Sitios Turísticos de un prestador.
    """
    serializer_class = SitioTuristicoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return SitioTuristico.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        serializer.save(perfil=self.request.user.perfil_prestador)

class ActividadEnSitioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las actividades dentro de un Sitio Turístico.
    La URL estará anidada bajo un sitio turístico específico para la creación y listado.
    Ej: /api/v1/mi-negocio/operativa/.../sitios-turisticos/{sitio_pk}/actividades/
    """
    serializer_class = ActividadEnSitioSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Filtra las actividades para que pertenezcan al sitio especificado en la URL,
        y verifica que ese sitio pertenezca al usuario logueado.
        """
        sitio_pk = self.kwargs.get('sitio_pk')
        return ActividadEnSitio.objects.filter(
            sitio__pk=sitio_pk,
            sitio__perfil=self.request.user.perfil_prestador
        )

    def perform_create(self, serializer):
        """
        Asigna la actividad al sitio turístico correcto basado en la URL.
        """
        sitio_pk = self.kwargs.get('sitio_pk')
        try:
            sitio = SitioTuristico.objects.get(pk=sitio_pk, perfil=self.request.user.perfil_prestador)
            serializer.save(sitio=sitio)
        except SitioTuristico.DoesNotExist:
            # Esto no debería pasar si los permisos están bien configurados, pero es una buena práctica.
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("El sitio turístico especificado no existe o no le pertenece.")
