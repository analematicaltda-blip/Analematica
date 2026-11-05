# SaritaUnificado/backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_genericos/perfil/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import ProviderProfile
from .serializers import PerfilSerializer, PerfilUpdateSerializer

class PerfilViewSet(viewsets.GenericViewSet):
    """
    ViewSet para que un prestador gestione su propio perfil.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # El queryset se filtra basado en el usuario, pero get_object se encarga de la lógica principal.
        return ProviderProfile.objects.filter(usuario=self.request.user)

    def get_object(self):
        # Devuelve el perfil asociado al usuario autenticado.
        # Lanza un 404 si no se encuentra.
        return self.request.user.perfil_prestador

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint para obtener el perfil del usuario autenticado.
        """
        try:
            instance = self.get_object()
            serializer = PerfilSerializer(instance)
            return Response(serializer.data)
        except ProviderProfile.DoesNotExist:
            return Response({"detail": "Perfil no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except AttributeError:
             return Response({"detail": "El usuario no tiene un perfil de prestador asociado."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['put', 'patch'], url_path='update-me', permission_classes=[IsAuthenticated])
    def update_me(self, request):
        """
        Endpoint para actualizar el perfil del usuario autenticado.
        """
        try:
            instance = self.get_object()
            serializer = PerfilUpdateSerializer(instance, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except ProviderProfile.DoesNotExist:
            return Response({"detail": "Perfil no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except AttributeError:
            return Response({"detail": "El usuario no tiene un perfil de prestador asociado."}, status=status.HTTP_404_NOT_FOUND)
