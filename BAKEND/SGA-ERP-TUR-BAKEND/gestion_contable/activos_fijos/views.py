from rest_framework import viewsets, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from .models import CategoriaActivo, ActivoFijo, CalculoDepreciacion
from .serializers import CategoriaActivoSerializer, ActivoFijoSerializer, CalculoDepreciacionSerializer
from .permissions import CanAssignOwnerPermission
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable, Transaccion, Cuenta

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Lógica actualizada para funcionar con el owner polimórfico
        if hasattr(obj, 'owner'):
            return obj.owner == request.user.perfil_prestador
        if hasattr(obj, 'activo'):
            return obj.activo.owner == request.user.perfil_prestador
        return False

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

class CategoriaActivoViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaActivoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner, CanAssignOwnerPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        profile = self.request.user.perfil_prestador
        content_type = ContentType.objects.get_for_model(profile)
        return CategoriaActivo.objects.filter(
            Q(owner_content_type=content_type, owner_object_id=profile.pk) |
            Q(perfil=profile)
        )

    def perform_create(self, serializer):
        # La lógica del owner se maneja en el serializer mixin si se proporciona.
        # Si no, se asigna el perfil del prestador actual.
        if not self.request.data.get('owner'):
            serializer.save(owner=self.request.user.perfil_prestador)
        else:
            # El mixin ya ha añadido owner_content_type y owner_object_id a validated_data
            serializer.save()

class ActivoFijoViewSet(viewsets.ModelViewSet):
    serializer_class = ActivoFijoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner, CanAssignOwnerPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        profile = self.request.user.perfil_prestador
        content_type = ContentType.objects.get_for_model(profile)
        return ActivoFijo.objects.filter(
            Q(owner_content_type=content_type, owner_object_id=profile.pk) |
            Q(perfil=profile)
        )

    def perform_create(self, serializer):
        if not serializer.validated_data.get('owner_content_type'):
            serializer.save(owner=self.request.user.perfil_prestador)
        else:
            serializer.save()

class CalculoDepreciacionViewSet(viewsets.ModelViewSet):
    serializer_class = CalculoDepreciacionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'post', 'head', 'options'] # Solo permitir crear y listar

    def get_queryset(self):
        return CalculoDepreciacion.objects.filter(activo__perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        depreciacion = serializer.save(creado_por=self.request.user)
        activo = depreciacion.activo
        provider = activo.owner # Asumiendo que el activo tiene un 'owner'

        # --- Creación del Asiento Contable de la Depreciación ---
        try:
            # Estas cuentas deberían ser configurables
            cuenta_gasto_dep = Cuenta.objects.get(codigo__startswith='5160', provider=provider)
            cuenta_dep_acum = Cuenta.objects.get(codigo__startswith='1592', provider=provider)
        except Cuenta.DoesNotExist:
            raise serializers.ValidationError(
                "No se encontraron las cuentas contables requeridas para la depreciación (Gasto '5160' o Dep. Acumulada '1592')."
            )

        asiento = AsientoContable.objects.create(
            provider=provider,
            fecha=depreciacion.fecha,
            descripcion=f"Depreciación de {activo.nombre}",
            creado_por=self.request.user,
        )

        # Débito a Gasto por Depreciación
        Transaccion.objects.create(asiento=asiento, cuenta=cuenta_gasto_dep, debito=depreciacion.monto)
        # Crédito a Depreciación Acumulada
        Transaccion.objects.create(asiento=asiento, cuenta=cuenta_dep_acum, credito=depreciacion.monto)
