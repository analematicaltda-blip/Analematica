from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from ..reports_engine import ReportsEngine

class BalanceGeneralView(APIView):
    """Bloque 3.4: Balance General por Tenant/Periodo."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cutoff_date = request.query_params.get('date')
        tenant_id = request.tenant_id # Inyectado por middleware

        data = ReportsEngine.get_balance_sheet(tenant_id, cutoff_date)
        return Response({
            "report": "Balance General",
            "date": cutoff_date,
            "currency": "COP",
            "totals": data,
            "status": "DETERMINISTIC_BACKEND_CALCULATED"
        })

class ProfitLossView(APIView):
    """Bloque 3.5: Estado de Resultados."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        data = ReportsEngine.get_p_and_l(request.tenant_id, start_date, end_date)
        return Response({
            "report": "Estado de Resultados",
            "period": f"{start_date} - {end_date}",
            "net_result": data['net_profit'],
            "details": data
        })
