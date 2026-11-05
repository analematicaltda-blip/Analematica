from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .serializers_factura import FacturaSerializer
from .models.FacturaElectronica import FacturaElectronica
from .dian_services import FacturacionElectronicaService
from django.core.mail import send_mail

class FacturaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FacturaElectronica.objects.all()
    serializer_class = FacturaSerializer

    @action(detail=True)
    def pdf(self, request, pk=None):
        factura = self.get_object()
        # Gen PDF from XML or store
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{factura.cufe}.pdf"'
        # PDF logic (reportlab/weasyprint)
        response.write(b'%PDF dummy')
        return response

    @action(detail=False, methods=['post'])
    def trigger_dian(self, request):
        op_id = request.data.get('operacion_id')
        factura, created = FacturaElectronica.objects.get_or_create(
            operacion_comercial_id=op_id,
            defaults={'prestador_email': 'prestador@test.com', 'tenant_id': request.tenant.id}
        )
        if created:
            FacturacionElectronicaService.procesar_envio_dian(factura)
            # Email
            send_mail(
                'Factura Generada',
                f'CUFE: {factura.cufe}',
                'noreply@sarita.co',
                [factura.prestador_email],
                attach_pdf=factura.pdf_url
            )
        return Response({'cufe': factura.cufe, 'estado': factura.estado_dian})
