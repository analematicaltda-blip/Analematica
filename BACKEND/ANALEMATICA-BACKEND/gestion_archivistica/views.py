from rest_framework import viewsets, permissions
from api.permissions import IsSuperAdmin
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from apps.admin_plataforma.gestion_archivistica.models import Document, DocumentVersion, Process, ProcessType, DocumentType
from .serializers import DocumentSerializer, AdminProcessSerializer

class DocumentViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    def perform_create(self, serializer):
        from apps.admin_plataforma.services.gestion_plataforma_service import GestionPlataformaService
        perfil_gobierno = GestionPlataformaService.get_perfil_gobierno()
        serializer.save(provider=perfil_gobierno)

class ProcessViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = AdminProcessSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ProcessTypeViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = ProcessType.objects.all()
    serializer_class = AdminProcessSerializer # Placeholder serializer or update it
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class DocumentTypeViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentSerializer # Placeholder serializer or update it
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
