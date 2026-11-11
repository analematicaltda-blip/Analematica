from rest_framework.response import Response
from ..reports_engine import ReportsEngine
from .report_access import AccountingReportView,report_company,dates,wire

class BalanceGeneralView(AccountingReportView):
    def get(self,request):
        with report_company(request) as company:
            cutoff=dates(request)
            data=ReportsEngine.get_balance_sheet(company.pk,cutoff)
            return Response(wire({'report':'Balance General','date':cutoff,'currency':company.currency,
                                  'totals':data,'status':'DETERMINISTIC_BACKEND_CALCULATED'}))

class ProfitLossView(AccountingReportView):
    def get(self,request):
        with report_company(request) as company:
            start,end=dates(request,interval=True)
            data=ReportsEngine.get_p_and_l(company.pk,start,end)
            return Response(wire({'report':'Estado de Resultados','period':f'{start} - {end}',
                                  'currency':company.currency,'net_result':data['net_profit'],'details':data}))
