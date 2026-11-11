from decimal import Decimal
from rest_framework.response import Response
from ..reports_engine import ReportsEngine
from .report_access import AccountingReportView,report_company,dates,wire

class FinancialRatiosView(AccountingReportView):
    def get(self,request):
        with report_company(request) as company:
            cutoff=dates(request)
            balance=ReportsEngine.get_balance_sheet(company.pk,cutoff)
            pnl=ReportsEngine.get_p_and_l(company.pk,cutoff.replace(day=1),cutoff)
            assets,liabilities=balance['assets'],balance['liabilities']
            income,profit=pnl['income'],pnl['net_profit']
            liquidity=assets/liabilities if liabilities>0 else None
            margin=profit/income if income>0 else None
            def ratio(value,label,status):
                return {'value':format(value.quantize(Decimal('0.0001')),'f') if value is not None else None,
                        'label':label,'status':status if value is not None else 'NOT_CALCULABLE'}
            return Response(wire({'currency':company.currency,'cutoff_date':cutoff,'read_only':True,
                'ratios':{
                    'liquidez':ratio(liquidity,'Ratio de activos a pasivos',
                        'HEALTHY' if liquidity is not None and liquidity>Decimal('1.5') else 'WARNING' if liquidity is not None and liquidity>1 else 'CRITICAL'),
                    'rentabilidad':ratio(margin,'Ratio de Rentabilidad','HEALTHY' if margin is not None and margin>Decimal('0.15') else 'STABLE'),
                    'margen_ganancia':ratio(margin,'Margen de Ganancia','STABLE')},
                'summary':{'total_assets':assets,'total_liabilities':liabilities,'net_income_month':profit},
                'snapshot':balance['snapshot']}))

class CashFlowView(AccountingReportView):
    def get(self,request):
        with report_company(request):
            dates(request,interval=True)
            # The engine intentionally refuses an unconfigured classification.
            return Response({'code':'CASH_FLOW_NOT_CONFIGURED','detail':'La clasificación de flujo de caja requiere configuración y conciliación.','read_only':True},status=501)
