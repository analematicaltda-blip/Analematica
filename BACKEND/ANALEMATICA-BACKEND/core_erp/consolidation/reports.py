from typing import Dict, Any, List
from decimal import Decimal
from .consolidation_engine import ConsolidationEngine
from .models import HoldingEntity, ConsolidatedReportSnapshot

class ConsolidationReports:
    """
    Generador de Reportes Financieros Consolidados.
    Capas: ReportBuilder
    """

    @staticmethod
    def get_consolidated_balance_sheet(holding_id: str, period: str = None) -> Dict[str, Any]:
        engine = ConsolidationEngine()
        tb = engine.generate_consolidated_trial_balance(holding_id, period)

        report = {
            'report_type': 'Consolidated Balance Sheet',
            'holding_name': tb['holding_name'],
            'cutoff_date': tb['cutoff_date'],
            'base_currency': tb['base_currency'],
            'assets': Decimal('0'),
            'liabilities': Decimal('0'),
            'equity': Decimal('0'),
            'details': tb['accounts']
        }

        for account in tb['accounts']:
            code = account['account_code']
            if code.startswith('1'):
                report['assets'] += account['balance']
            elif code.startswith('2'):
                report['liabilities'] += account['balance']
            elif code.startswith('3'):
                report['equity'] += account['balance']

        report['check'] = report['assets'] - (report['liabilities'] + report['equity'])

        # Guardar snapshot inmutable
        ConsolidationReports.save_snapshot(holding_id, 'BALANCE_SHEET', tb['cutoff_date'], report)

        return report

    @staticmethod
    def get_consolidated_income_statement(holding_id: str, period: str = None) -> Dict[str, Any]:
        engine = ConsolidationEngine()
        tb = engine.generate_consolidated_trial_balance(holding_id, period)

        report = {
            'report_type': 'Consolidated Income Statement',
            'holding_name': tb['holding_name'],
            'cutoff_date': tb['cutoff_date'],
            'base_currency': tb['base_currency'],
            'income': Decimal('0'),
            'expenses': Decimal('0'),
            'details': tb['accounts']
        }

        for account in tb['accounts']:
            code = account['account_code']
            if code.startswith('4'):
                report['income'] += account['balance']
            elif code.startswith('5'):
                report['expenses'] += account['balance']

        report['net_income'] = report['income'] - report['expenses']

        # Guardar snapshot
        ConsolidationReports.save_snapshot(holding_id, 'INCOME_STATEMENT', tb['cutoff_date'], report)

        return report

    @staticmethod
    def save_snapshot(holding_id: str, report_type: str, period: str, data: Dict[str, Any]):
        holding = HoldingEntity.objects.get(id=holding_id)

        import json
        from decimal import Decimal

        class DecimalEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Decimal):
                    return str(obj)
                return super(DecimalEncoder, self).default(obj)

        json_data = json.loads(json.dumps(data, cls=DecimalEncoder))

        ConsolidatedReportSnapshot.objects.create(
            holding=holding,
            report_type=report_type,
            period=period,
            fx_rates_used={}, # Capturar tasas reales en implementación prod
            tenants_included=[str(m.tenant.id) for m in holding.memberships.all()],
            data=json_data,
            method_applied="MULTI_LAYER_AGGREGATION"
        )
