from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from ..services.reportes import FinancialReportService

class BalanceGeneralView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        periodo_id = request.query_params.get('periodo_id')
        if not periodo_id:
            return Response({"error": "Se requiere 'periodo_id'."}, status=400)

        perfil_id = request.user.perfil_prestador.id
        data = FinancialReportService.generar_balance_general(periodo_id, perfil_id)

        if data:
            return Response(data)
        return Response({"error": "No se pudo generar el reporte."}, status=500)
