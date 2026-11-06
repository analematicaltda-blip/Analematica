from rest_framework import viewsets, permissions, decorators, response
from django.http import HttpResponse
from .models import Supplier, PurchaseInvoice
from .serializers import SupplierSerializer, PurchaseInvoiceSerializer
from .services import ProcurementService
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class SupplierViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class PurchaseInvoiceViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = PurchaseInvoice.objects.all()
    serializer_class = PurchaseInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    @decorators.action(detail=False, methods=['post'], url_path='massive-payment')
    def massive_payment(self, request):
        """
        Generates payment CSV for selected invoices.
        """
        invoice_ids = request.data.get('invoice_ids', [])
        csv_content = ProcurementService.generate_massive_payment_file(
            request.tenant_id, invoice_ids
        )

        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="massive_payment.csv"'
        return response

    @decorators.action(detail=True, methods=['post'], url_path='pay')
    def process_payment(self, request, pk=None):
        """
        Registers individual payment.
        """
        invoice = ProcurementService.process_supplier_payment(
            request.tenant_id,
            pk,
            request.data.get('amount'),
            request.data.get('bank_reference')
        )
        return response.Response({"status": "PAID", "invoice_id": invoice.id})
