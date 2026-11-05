from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from .models import Documento

class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        return super().get_queryset().filter(prestador_ref_id=self.request.tenant.id)

    def perform_create(self, serializer):
        serializer.save(prestador_ref_id=self.request.tenant.id)
        # Trigger OCR AI
        self.ocr_document(serializer.instance)

    def ocr_document(self, doc):
        # AI OCR service call
        pass

    @action(detail=True)
    def versions(self, request, pk):
        doc = self.get_object()
        return Response([{'version': v.version} for v in doc.versions.all()])

