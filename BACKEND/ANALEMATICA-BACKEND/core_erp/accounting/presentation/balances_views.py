from rest_framework import serializers
from rest_framework.response import Response
from ..reports_engine import ReportsEngine
from .report_access import AccountingReportView,report_company,dates,wire

class AccountBalanceSerializer(serializers.Serializer):
    account_id=serializers.UUIDField()
    account_code=serializers.CharField()
    account_name=serializers.CharField()
    debit=serializers.DecimalField(max_digits=28,decimal_places=2)
    credit=serializers.DecimalField(max_digits=28,decimal_places=2)
    balance=serializers.DecimalField(max_digits=28,decimal_places=2)

class AccountBalanceView(AccountingReportView):
    def get(self,request):
        with report_company(request) as company:
            cutoff=dates(request)
            report=ReportsEngine.get_account_balances(company.pk,cutoff)
            return Response(wire(report['lines']))
