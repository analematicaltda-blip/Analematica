from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tax, TaxRule, TaxRate, TaxTransaction
from .tax_engine import TaxEngine
from .accounting_bridge import TaxLedgerBridge

class TaxViewSet(viewsets.ModelViewSet):
    """Bloque 4: Gestión de Impuestos y Reglas."""
    queryset = Tax.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """POST /api/tax/calculate"""
        payload = request.data
        payload['tenant_id'] = request.user.tenant_id # Forzar tenant por sesión

        try:
            taxes = TaxEngine.calculate_taxes(payload)
            # Integrar contabilidad inmediatamente si el flag está activo
            if payload.get('post_to_ledger', True):
                TaxLedgerBridge.post_taxes_to_accounting(payload['document_id'], payload['tenant_id'])

            return Response({
                "document_id": payload['document_id'],
                "taxes": taxes,
                "total_tax": sum(t['amount'] for t in taxes),
                "accounting_synced": True
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary_report(self, request):
        """GET /api/tax/report/summary"""
        period = request.query_params.get('period')
        # Lógica de agregación por periodo y tenant
        return Response({"period": period, "total_vat": 0, "total_withholding": 0})
