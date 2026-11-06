
from rest_framework import viewsets, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema
from .services.gestion_plataforma_service import GestionPlataformaService
from .services.governance_kernel import GovernanceKernel
from apps.comercial.models import Plan, Subscription
from .serializers import PlanSerializer, SuscripcionSerializer
from apps.domain_business.operativa.presentation.serializers import PerfilSerializer
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class MetaStandardView(APIView):
    """
    Vista para obtener la doctrina de la FASE META (Estándar SARITA).
    """
    permission_classes = [IsAdminUser]

    @extend_schema(responses={200: serializers.JSONField()})
    def get(self, request):
        kernel = GovernanceKernel(user=request.user)
        metadata = kernel.get_meta_standard_metadata()
        return Response(metadata)

class SaritaProfileView(APIView):
    """
    Vista para obtener el perfil empresarial de la Plataforma Sarita.
    """
    permission_classes = [IsAdminUser]
    serializer_class = PerfilSerializer

    def get(self, request):
        """
        Devuelve los detalles del perfil de la plataforma Sarita.
        """
        service = GestionPlataformaService(admin_user=request.user)
        sarita_profile = service.get_sarita_profile()
        serializer = PerfilSerializer(sarita_profile)
        return Response(serializer.data)

class PlanViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet para la gestión de Planes de suscripción por parte de los administradores.
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        # Delegar toda decisión al núcleo de orquestación
        kernel = GovernanceKernel(user=self.request.user)
        result = kernel.resolve_and_execute(
            intention_name="PLATFORM_CREATE_PLAN",
            parameters=serializer.validated_data
        )
        # Asignar la instancia creada al serializer para que la respuesta sea correcta
        serializer.instance = result.get("instance")

class SuscripcionViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet para la gestión de Suscripciones de clientes a planes.
    """
    queryset = Subscription.objects.all()
    serializer_class = SuscripcionSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        plan = serializer.validated_data['plan']
        perfil_ref_id = serializer.validated_data['perfil_ref_id']
        start_date = serializer.validated_data.get('start_date')

        service = GestionPlataformaService(admin_user=self.request.user)
        service.asignar_suscripcion(perfil_ref_id=perfil_ref_id, plan=plan, start_date=start_date)

class SupervisionDianViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Panel de Supervisión DIAN para el Super Administrador.
    Permite ver el estado de facturación de todos los prestadores en tiempo real.
    """
    permission_classes = [IsSuperAdmin]

    def list(self, request):
        from django.utils.module_loading import import_string
        FacturaVenta = import_string('apps.prestadores.mi_negocio.gestion_comercial.domain.models.FacturaVenta') # DECOUPLED
        from django.db.models import Count

        stats = FacturaVenta.objects.values('estado_dian').annotate(total=Count('id'))
        last_invoices = FacturaVenta.objects.select_related('operacion').order_by('-id')[:20]

        return Response({
            "resumen_ejecutivo": stats,
            "ultimas_facturas": [
                {
                    "id": f.id,
                    "numero": f.number,
                    "tenant_id": f.perfil_ref_id,
                    "estado_dian": f.estado_dian,
                    "total": f.total,
                    "cufe": f.cufe
                } for f in last_invoices
            ]
        })
