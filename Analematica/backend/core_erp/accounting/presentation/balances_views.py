from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum
from ..models import Account, LedgerEntry

class AccountBalanceSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    account_code = serializers.CharField()
    account_name = serializers.CharField()
    debit = serializers.DecimalField(max_digits=18, decimal_places=2)
    credit = serializers.DecimalField(max_digits=18, decimal_places=2)
    balance = serializers.DecimalField(max_digits=18, decimal_places=2)

class AccountBalanceView(APIView):
    """
    Hallazgo 14: Hidratación de saldos contables reales.
    Proporciona los saldos agregados de todas las cuentas del tenant.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # El queryset ya está filtrado por tenant vía GlobalTenantManager si se usa .objects.all()
        # en modelos que heredan de TenantAwareModel
        accounts = Account.objects.all()
        result = []

        for account in accounts:
            # Calcular agregados
            totals = LedgerEntry.objects.filter(account=account).aggregate(
                total_debit=Sum('debit_amount'),
                total_credit=Sum('credit_amount')
            )

            debit = totals['total_debit'] or 0
            credit = totals['total_credit'] or 0

            # El balance depende del tipo de cuenta (Deudora vs Acreedora)
            # Simplificación: Debito - Crédito
            balance = debit - credit

            result.append({
                "account_id": account.id,
                "account_code": account.code,
                "account_name": account.name,
                "debit": debit,
                "credit": credit,
                "balance": balance
            })

        serializer = AccountBalanceSerializer(result, many=True)
        return Response(serializer.data)
