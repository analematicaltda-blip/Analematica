from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from ..reports_engine import ReportsEngine
from decimal import Decimal

class FinancialRatiosView(APIView):
    """
    Bloque 11: Ratios Financieros (Liquidez, Rentabilidad, etc.)
    Cálculo 100% en Backend.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tenant_id = request.tenant_id
        cutoff_date = request.query_params.get('date')

        # 1. Obtener datos base
        balance = ReportsEngine.get_balance_sheet(tenant_id, cutoff_date)
        # Para P&L tomamos el mes actual
        from datetime import datetime
        now = datetime.now()
        start_month = now.replace(day=1).strftime('%Y-%m-%d')
        end_month = now.strftime('%Y-%m-%d')
        pnl = ReportsEngine.get_p_and_l(tenant_id, start_month, end_month)

        # 2. Calcular Ratios
        # Liquidez = Activos / Pasivos
        assets = Decimal(str(balance['assets']))
        liabilities = Decimal(str(balance['liabilities']))
        liquidez = assets / liabilities if liabilities > 0 else Decimal('0.00')

        # Rentabilidad = Utilidad Neta / Ingresos
        income = Decimal(str(pnl['income']))
        profit = Decimal(str(pnl['net_profit']))
        rentabilidad = profit / income if income > 0 else Decimal('0.00')

        # Margen = (Ingresos - Costos) / Ingresos (Simplificado aquí como Rentabilidad en este nivel)
        margen = rentabilidad

        return Response({
            "ratios": {
                "liquidez": {
                    "value": round(float(liquidez), 2),
                    "label": "Ratio de Liquidez",
                    "status": "HEALTHY" if liquidez > 1.5 else "WARNING" if liquidez > 1.0 else "CRITICAL"
                },
                "rentabilidad": {
                    "value": round(float(rentabilidad), 2),
                    "label": "Ratio de Rentabilidad",
                    "status": "HEALTHY" if rentabilidad > 0.15 else "STABLE"
                },
                "margen_ganancia": {
                    "value": round(float(margen), 2),
                    "label": "Margen de Ganancia",
                    "status": "STABLE"
                }
            },
            "summary": {
                "total_assets": balance['assets'],
                "total_liabilities": balance['liabilities'],
                "net_income_month": pnl['net_profit']
            }
        })

class CashFlowView(APIView):
    """Bloque 11.2: Flujo de Caja Mensual."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tenant_id = request.tenant_id
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        data = ReportsEngine.get_cash_flow(tenant_id, start_date, end_date)

        return Response({
            "report": "Flujo de Caja",
            "period": f"{start_date} - {end_date}",
            "data": data,
            "net_cash": data['net_increase_cash']
        })
