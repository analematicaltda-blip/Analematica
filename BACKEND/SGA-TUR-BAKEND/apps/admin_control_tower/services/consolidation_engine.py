import logging
from decimal import Decimal
from django.db.models import Sum, Q
from apps.admin_plataforma.gestion_contable.contabilidad.models import (
    AdminJournalEntry, AdminAccountingTransaction, AdminAccount, AdminFiscalPeriod
)
from apps.comercial.models import Subscription, Plan
from apps.comercial.saas_metrics.revenue_metrics import RevenueMetrics
from apps.comercial.saas_metrics.churn_analysis import ChurnAnalysis

logger = logging.getLogger(__name__)

class ConsolidationEngine:
    """
    Motor de agregación financiera para la Holding Sarita.
    Genera reportes consolidados en tiempo real desde el ERP Admin.
    """

    @staticmethod
    def get_balance_sheet():
        """
        Genera el Balance General (Activo, Pasivo, Patrimonio).
        """
        accounts = AdminAccount.objects.all()

        # Agregamos saldos por tipo de cuenta
        # Nota: En una implementación real, esto consideraría la naturaleza (débito/crédito)
        assets = AdminAccountingTransaction.objects.filter(account__account_type='ASSET').aggregate(
            total_debit=Sum('debit'), total_credit=Sum('credit')
        )
        liabilities = AdminAccountingTransaction.objects.filter(account__account_type='LIABILITY').aggregate(
            total_debit=Sum('debit'), total_credit=Sum('credit')
        )
        equity = AdminAccountingTransaction.objects.filter(account__account_type='EQUITY').aggregate(
            total_debit=Sum('debit'), total_credit=Sum('credit')
        )

        def calc_balance(agg):
             return (agg['total_debit'] or 0) - (agg['total_credit'] or 0)

        return {
            "assets": calc_balance(assets),
            "liabilities": -calc_balance(liabilities), # Pasivo aumenta con crédito
            "equity": -calc_balance(equity), # Patrimonio aumenta con crédito
        }

    @staticmethod
    def get_income_statement(period_name=None):
        """
        Genera el Estado de Resultados (Ingresos - Gastos).
        """
        query = Q()
        if period_name:
            query &= Q(journal_entry__period__name=period_name)

        revenue = AdminAccountingTransaction.objects.filter(
            query, account__account_type='REVENUE'
        ).aggregate(total_debit=Sum('debit'), total_credit=Sum('credit'))

        expenses = AdminAccountingTransaction.objects.filter(
            query, account__account_type='EXPENSE'
        ).aggregate(total_debit=Sum('debit'), total_credit=Sum('credit'))

        rev_val = (revenue['total_credit'] or 0) - (revenue['total_debit'] or 0)
        exp_val = (expenses['total_debit'] or 0) - (expenses['total_credit'] or 0)

        return {
            "revenue": rev_val,
            "expenses": exp_val,
            "net_income": rev_val - exp_val
        }

    @staticmethod
    def get_saas_metrics():
        """
        Calcula KPIs de SaaS (MRR, ARR, Churn, LTV, ARPU).
        """
        mrr = RevenueMetrics.calculate_mrr()
        churn = ChurnAnalysis.calculate_churn_rate()

        return {
            "mrr": mrr,
            "arr": mrr * 12,
            "active_tenants": Subscription.objects.filter(status=Subscription.Status.ACTIVE).count(),
            "churn_rate": churn,
            "arpu": RevenueMetrics.calculate_arpu(),
            "ltv": RevenueMetrics.calculate_ltv(churn)
        }
