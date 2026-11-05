from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Funnel, FunnelVersion, FunnelPage, FunnelPublication
from .serializers import FunnelSerializer, FunnelVersionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .models import LeadCapture, FunnelEvent
 
try:
    from shared.services import event_dispatcher
except (ImportError, ValueError):
    from ..shared.services import event_dispatcher
 


class LeadCaptureView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={201: {"type": "object", "properties": {"status": {"type": "string"}}}})
    def post(self, request, slug, *args, **kwargs):
        try:
            publication = FunnelPublication.objects.get(public_url_slug=slug, is_active=True)
        except FunnelPublication.DoesNotExist:
            return Response({"error": "Funnel no encontrado."}, status=404)

        form_data = request.data.get('form_data', {})
        page_id = request.data.get('page_id')

        if not page_id:
            return Response({"error": "El campo 'page_id' es requerido."}, status=400)

 
        lead = LeadCapture.objects.create(
 
            funnel=publication.funnel,
            version=publication.version,
            page_id=page_id,
            form_data=form_data
        )
 

        # Emitir el evento de dominio
        event_dispatcher.dispatch(
            'lead.created',
            {
                'lead_id': lead.id,
                'funnel_id': lead.funnel.id,
                'version_id': lead.version.id,
                'tenant_id': lead.funnel.tenant_id,
                'form_data': lead.form_data,
            }
        )

        # --- INTEGRACIÓN CON AGENTES SARITA ---
        try:
            from apps.sarita_agents.orchestrator import sarita_orchestrator
            directive = {
                "domain": "prestadores",
                "mission": {
                    "type": "AVANZAR_LEAD",
                    "params": {
                        "lead_id": str(lead.id),
                        "form_data": lead.form_data,
                        "source": "funnel_capture"
                    }
                }
            }
            sarita_orchestrator.handle_directive(directive)
        except Exception as e:
            # No bloqueamos el flujo principal si el agente falla en el capture inicial
            print(f"Error delegando captura de lead a Sarita: {e}")

 
        return Response({"status": "Lead capturado exitosamente y delegado a Sarita."}, status=201)


class FunnelEventView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={202: None})
    def post(self, request, *args, **kwargs):
        funnel_id = request.data.get('funnel_id')
        version_id = request.data.get('version_id')
        event_type = request.data.get('event_type')
        metadata = request.data.get('metadata', {})

        if not all([funnel_id, version_id, event_type]):
            return Response({"error": "Los campos 'funnel_id', 'version_id', y 'event_type' son requeridos."}, status=400)

        FunnelEvent.objects.create(
            funnel_id=funnel_id,
            version_id=version_id,
            event_type=event_type,
            metadata_json=metadata
        )
        return Response(status=202)


class PublicFunnelView(APIView):
    authentication_classes = [] # Sin autenticación
    permission_classes = []

    @extend_schema(responses={200: FunnelVersionSerializer})
    def get(self, request, slug, *args, **kwargs):
        try:
            publication = FunnelPublication.objects.select_related('version').get(public_url_slug=slug, is_active=True)
            serializer = FunnelVersionSerializer(publication.version)
            return Response(serializer.data)
        except FunnelPublication.DoesNotExist:
            return Response({"error": "Funnel no encontrado o no está publicado."}, status=404)


class FunnelViewSet(viewsets.ModelViewSet):
    queryset = Funnel.objects.all().prefetch_related('versions')
    serializer_class = FunnelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil_prestador'):
             return self.queryset.filter(tenant__name=user.perfil_prestador.nombre_comercial)
        if hasattr(user, 'tenant'):
             return self.queryset.filter(tenant=user.tenant)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        tenant = None
        if hasattr(user, 'perfil_prestador'):
            from ..infrastructure.models import Tenant
            tenant, _ = Tenant.objects.get_or_create(name=user.perfil_prestador.nombre_comercial)
        elif hasattr(user, 'tenant'):
            tenant = user.tenant

        funnel = serializer.save(tenant=tenant)
        # Al crear un funnel, creamos una primera versión vacía
        FunnelVersion.objects.create(funnel=funnel, version_number=1, schema_json={}, is_active=True)

    @action(detail=True, methods=['post'], url_path='versions')
    @transaction.atomic
    def create_version(self, request, pk=None):
        funnel = self.get_object()
        schema_json = request.data.get('schema_json')
        pages_data = request.data.get('pages', [])

        if not schema_json:
            return Response({"error": "El campo 'schema_json' es requerido."}, status=400)

        # Calculamos el nuevo número de versión
        latest_version = funnel.versions.first()
        new_version_number = (latest_version.version_number + 1) if latest_version else 1

        # Creamos la nueva versión
        new_version = FunnelVersion.objects.create(
            funnel=funnel,
            version_number=new_version_number,
            schema_json=schema_json
        )

        # Creamos las páginas asociadas
        for index, page_data in enumerate(pages_data):
            FunnelPage.objects.create(
                funnel_version=new_version,
                page_type=page_data.get('page_type', 'default'),
                page_schema_json=page_data.get('page_schema_json', {}),
                order_index=index
            )

        serializer = FunnelVersionSerializer(new_version)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['post'], url_path='publish')
    @transaction.atomic
    def publish(self, request, pk=None):
        funnel = self.get_object()
        version_id = request.data.get('version_id')

        if not version_id:
            return Response({"error": "El campo 'version_id' es requerido."}, status=400)

        try:
            version_to_publish = funnel.versions.get(id=version_id)
        except FunnelVersion.DoesNotExist:
            return Response({"error": "La versión especificada no existe para este funnel."}, status=404)

        # Desactivar publicaciones anteriores de este funnel
        funnel.publications.update(is_active=False)

        # Crear la nueva publicación
        publication = FunnelPublication.objects.create(
            funnel=funnel,
            version=version_to_publish,
            is_active=True
        )

        # Actualizar el estado del funnel
        funnel.status = 'published'
        funnel.save()

        return Response({
            "status": "Funnel publicado exitosamente.",
            "public_url": f"/f/{publication.public_url_slug}" # URL relativa
        }, status=200)


class FunnelEditorDataView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: {"type": "object"}})
    def get(self, request, *args, **kwargs):
        # NOTA: En un sistema real, esto filtraría por Tenant.
        # Para la Fase 1 de Sarita, consolidamos la vista del prestador.
        from .models import CadenaTurismo, FunnelCategoria, FunnelSubcategoria, FunnelLandingPage

        cadenas = CadenaTurismo.objects.all()
        # Mapeo simple para la UI del Arquitecto
        data = {
            "cadenas": [{"id": c.id, "nombre": c.nombre, "color_primario": c.color_primario} for c in cadenas],
            "categorias": [{"id": c.id, "nombre": c.nombre, "cadenaId": c.cadena_id} for c in FunnelCategoria.objects.all()],
            "subcategorias": [{"id": s.id, "nombre": s.nombre, "categoriaId": s.categoria_id} for s in FunnelSubcategoria.objects.all()],
            "landingPages": [
                {
                    "id": lp.id,
                    "nombre": lp.nombre,
                    "subcategoriaId": lp.subcategoria_id,
                    "funnels": FunnelSerializer(lp.funnels.all(), many=True).data
                } for lp in FunnelLandingPage.objects.all()
            ],
            "mediaLibrary": [] # Placeholder
        }
        return Response(data)
