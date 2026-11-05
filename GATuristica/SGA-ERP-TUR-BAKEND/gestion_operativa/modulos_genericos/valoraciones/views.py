from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Valoracion
from .serializers import ValoracionSerializer, RespuestaPrestadorSerializer
from apps.prestadores.mi_negocio.permissions import IsPrestadorOwner
from api.permissions import IsTurista

class ValoracionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las Valoraciones.
    - Turistas pueden crear valoraciones (POST).
    - Prestadores pueden ver las valoraciones de sus productos (GET) y responderlas (PATCH/PUT).
    - Todos pueden ver las valoraciones de un producto (GET).
    """
    serializer_class = ValoracionSerializer

    def get_queryset(self):
        """
        Filtra las valoraciones basadas en el rol del usuario.
        - Si es prestador, ve las valoraciones de sus productos.
        - Si no, ve todas las valoraciones (se podría restringir más si es necesario).
        """
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'perfil_prestador'):
            return Valoracion.objects.filter(perfil_prestador=user.perfil_prestador)

        # Filtra por producto si se pasa como query param
        producto_id = self.request.query_params.get('producto_id')
        if producto_id:
            return Valoracion.objects.filter(producto_id=producto_id)

        return Valoracion.objects.all()

    def get_permissions(self):
        """
        Define permisos por acción:
        - `create`: Solo turistas autenticados.
        - `responder`: Solo el prestador dueño de la valoración.
        - `list`, `retrieve`: Cualquiera (público).
        - `update`, `partial_update`, `destroy`: Deshabilitado por ahora para simplificar.
        """
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, IsTurista]
        elif self.action == 'responder':
            self.permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        producto = serializer.validated_data['producto']
        serializer.save(
            turista=self.request.user,
            perfil_prestador=producto.perfil
        )

    @action(detail=True, methods=['patch'], url_path='responder', serializer_class=RespuestaPrestadorSerializer)
    def responder(self, request, pk=None):
        """
        Acción personalizada para que un prestador responda a una valoración.
        """
        valoracion = self.get_object()

        # Verificación extra de que el prestador es el dueño
        if valoracion.perfil_prestador != request.user.perfil_prestador:
            return Response(
                {"error": "No tiene permiso para responder a esta valoración."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(valoracion, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(fecha_respuesta=timezone.now())

        # Devolvemos la valoración completa con la respuesta incluida
        full_serializer = ValoracionSerializer(valoracion)
        return Response(full_serializer.data)
