from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from .models import Document, DocumentVersion, Process, ProcessType, DocumentType
from .services.logic_services import DocumentCoordinatorService
from .services.file_service import FileCoordinator
from .serializers import (
    DocumentListSerializer, DocumentDetailSerializer, DocumentCreateSerializer,
    DocumentVersionCreateSerializer, DocumentVersionSerializer,
    ProcessTypeSerializer, ProcessSerializer, DocumentTypeSerializer
)

# ==========================================================
# ViewSets para Catálogos (Solo Lectura)
# ==========================================================
class CompanyCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtra los catálogos para que solo pertenezcan a la compañía del usuario actual.
        # Se asume que el request.user tiene un perfil con una compañía asociada.
        return self.queryset.filter(company=self.request.user.perfil_prestador.company)

class ProcessTypeViewSet(CompanyCatalogViewSet):
    queryset = ProcessType.objects.all()
    serializer_class = ProcessTypeSerializer

class ProcessViewSet(CompanyCatalogViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        process_type_id = self.request.query_params.get('process_type_id')
        if process_type_id:
            return queryset.filter(process_type_id=process_type_id)
        return queryset

class DocumentTypeViewSet(CompanyCatalogViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer

# ==========================================================
# ViewSet Principal de Documentos
# ==========================================================
class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Solo retorna documentos de la compañía del usuario
        qs = Document.objects.filter(company=self.request.user.perfil_prestador.company)

        # Auditoría de consulta de catálogo
        if self.action == 'list':
            from .sargentos import SargentoArchivistico
            SargentoArchivistico.registrar_acceso(None, self.request.user.id, action="LIST_CATALOG")

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        if self.action == 'create':
            return DocumentCreateSerializer
        return DocumentDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = request.data.get('file')
        if not file_obj:
            return Response({"file": ["Este campo es requerido."]}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        validated_data['original_filename'] = file_obj.name
        file_content = file_obj.read()

        try:
            version = DocumentCoordinatorService.create_document_and_first_version(
                data=validated_data,
                user=request.user.perfil_prestador,
                file_content=file_content,
                request=request
            )
            # Usamos el DocumentDetailSerializer para devolver el objeto Document completo
            response_serializer = DocumentDetailSerializer(version.document, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Log the exception e
            return Response({"error": f"An internal error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='versions/(?P<version_pk>\\d+)/download')
    def download_version(self, request, pk=None, version_pk=None):
        document = self.get_object()
        version = get_object_or_404(document.versions, pk=version_pk)

        if not version.external_file_id or version.status == 'PENDING_UPLOAD':
            return Response({"error": "File is still processing."}, status=status.HTTP_404_NOT_FOUND)

        try:
            coordinator = FileCoordinator()
            file_content = coordinator.download(version)

            # --- AUDITORÍA ARCHIVÍSTICA VÍA SARGENTO ---
            from .sargentos import SargentoArchivistico
            SargentoArchivistico.registrar_acceso(document.id, request.user.id, action="DOWNLOAD")

            response = HttpResponse(file_content, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{version.original_filename}"'
            return response
        except FileNotFoundError:
            return Response({"error": "File not found in storage."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log the exception e
            return Response({"error": "Could not decrypt or retrieve the file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='versions')
    def create_version(self, request, pk=None):
        document = self.get_object()
        serializer = DocumentVersionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = request.data.get('file')
        if not file_obj:
            return Response({"file": ["Este campo es requerido."]}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        validated_data['original_filename'] = file_obj.name
        file_content = file_obj.read()

        try:
            new_version = DocumentCoordinatorService.create_new_version_for_document(
                document=document,
                data=validated_data,
                user=request.user.perfil_prestador,
                file_content=file_content,
                request=request
            )
            response_serializer = DocumentVersionSerializer(new_version)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Log the exception e
            return Response({"error": f"An internal error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
