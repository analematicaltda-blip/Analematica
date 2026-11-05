import logging
from .models import LegalEntity, IntercompanyTransaction, CorporateHolding
from apps.core_erp.accounting_engine import AccountingEngine
from decimal import Decimal
from django.db.models import Sum

logger = logging.getLogger(__name__)

class ConsolidationEngine:
    """
    Aggregates financial data across multiple entities and performs eliminations.
    """

    @staticmethod
    def consolidate_holding(holding_id):
        holding = CorporateHolding.objects.get(id=holding_id)
        entities = holding.entities.all()

        consolidated_data = {
            'revenue': Decimal('0.00'),
            'expenses': Decimal('0.00'),
            'ebitda': Decimal('0.00'),
            'assets': Decimal('0.00'),
            'liabilities': Decimal('0.00'),
            'equity': Decimal('0.00'),
            'eliminations': Decimal('0.00')
        }

        # 1. Aggregate Raw Data
        for entity in entities:
            entity_fin = ConsolidationEngine._get_entity_financials(entity)
            consolidated_data['revenue'] += entity_fin['revenue']
            consolidated_data['expenses'] += entity_fin['expenses']
            consolidated_data['assets'] += entity_fin['assets']
            consolidated_data['liabilities'] += entity_fin['liabilities']

        # 2. Perform Intercompany Eliminations
        # Total mirrored intercompany transactions should be subtracted from both revenue and expenses
        intercompany_txs = IntercompanyTransaction.objects.filter(
            source_entity__parent_holding=holding,
            destination_entity__parent_holding=holding,
            is_mirrored=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        consolidated_data['revenue'] -= intercompany_txs
        consolidated_data['expenses'] -= intercompany_txs
        consolidated_data['eliminations'] = intercompany_txs

        # 3. Final Calculations
        consolidated_data['ebitda'] = consolidated_data['revenue'] - consolidated_data['expenses']
        consolidated_data['equity'] = consolidated_data['assets'] - consolidated_data['liabilities']

        return consolidated_data

    @staticmethod
    def _get_entity_financials(entity):
        # In production: Fetch from ERP Ledger using AccountingEngine
        # For Phase A1: Mocking based on entity type
        if entity.entity_type == 'OPERATING':
            return {'revenue': Decimal('1000000.00'), 'expenses': Decimal('600000.00'), 'assets': Decimal('500000.00'), 'liabilities': Decimal('100000.00')}
        if entity.entity_type == 'IP_CO':
            return {'revenue': Decimal('100000.00'), 'expenses': Decimal('10000.00'), 'assets': Decimal('1000000.00'), 'liabilities': Decimal('0.00')}

        return {'revenue': Decimal('0.00'), 'expenses': Decimal('0.00'), 'assets': Decimal('0.00'), 'liabilities': Decimal('0.00')}
