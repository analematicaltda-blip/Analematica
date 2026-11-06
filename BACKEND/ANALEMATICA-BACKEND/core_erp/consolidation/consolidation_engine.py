import logging
from decimal import Decimal
from typing import Dict, List, Any
from django.utils import timezone
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from .models import HoldingEntity, HoldingMembership
from .currency_translation import CurrencyTranslation
from .elimination_rules import IntercompanyEliminator

logger = logging.getLogger(__name__)

class ConsolidationEngine:
    """
    Motor de Consolidación Financiera del Core ERP.
    Agregación virtual siguiendo arquitectura de 5 capas:
    1. TenantCollector
    2. TrialBalanceAggregator
    3. CurrencyTranslator
    4. IntercompanyEliminator
    5. ConsolidationApplier
    """

    def generate_consolidated_trial_balance(self, holding_id: str, period: str = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Flujo maestro de consolidación.
        Implementa optimizaciones: incremental snapshots y cache inteligente (Fase 6.4).
        """
        holding = self._load_holding(holding_id)

        # 1. Intento de recuperación desde Cache/Snapshot (Fase 6.4.3)
        if use_cache and period:
            from .models import ConsolidatedReportSnapshot
            cached = ConsolidatedReportSnapshot.objects.filter(
                holding=holding,
                report_type='TRIAL_BALANCE',
                period=period
            ).order_by('-generated_at').first()
            if cached:
                logger.info(f"Consolidación recuperada desde Snapshot para el periodo {period}")
                return cached.data

        tenants_memberships = self._collect_tenants(holding)
        individual_balances = []
        cutoff_date = timezone.now().date() # Simplificado para el periodo

        # 2. Procesamiento Paralelo (Simulado con hilos para escalabilidad)
        # En prod se usaría Celery chords o multiproc.
        import concurrent.futures

        def get_tenant_data(membership):
            tenant = membership.tenant
            # 1. Obtener trial balance individual
            tb = LedgerEngine.get_trial_balance(str(tenant.id), cutoff_date)
            # 2. Convertir moneda
            translated_tb = self._translate_currency(
                tb, from_currency=tenant.currency, to_currency=holding.base_currency, period=period
            )
            # 3. Aplicar método
            return self._apply_consolidation_method(
                translated_tb, membership.ownership_percentage, membership.consolidation_method
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_tenant = {executor.submit(get_tenant_data, m): m for m in tenants_memberships}
            for future in concurrent.futures.as_completed(future_to_tenant):
                res = future.result()
                if res:
                    individual_balances.append(res)

        # 3. Agregación (TrialBalanceAggregator)
        aggregated = self._aggregate_balances(individual_balances)

        # 5. Eliminación Intercompany (IntercompanyEliminator)
        eliminated = IntercompanyEliminator.execute(aggregated, holding_id)

        return self._build_trial_balance_report(holding, eliminated, cutoff_date)

    def _load_holding(self, holding_id: str) -> HoldingEntity:
        return HoldingEntity.objects.get(id=holding_id)

    def _collect_tenants(self, holding: HoldingEntity) -> List[HoldingMembership]:
        memberships = holding.memberships.all()
        if not memberships.exists():
            raise ValueError(f"El holding {holding.name} no tiene tenants asociados.")
        return list(memberships)

    def _translate_currency(self, tb: Dict[str, Any], from_currency: str, to_currency: str, period: str = None) -> Dict[str, Any]:
        if from_currency == to_currency:
            return tb

        rate = CurrencyTranslation.get_rate(from_currency, to_currency, period)
        for line in tb['lines']:
            line['debit'] = CurrencyTranslation.translate(line['debit'], from_currency, to_currency, rate)
            line['credit'] = CurrencyTranslation.translate(line['credit'], from_currency, to_currency, rate)
            line['balance'] = CurrencyTranslation.translate(line['balance'], from_currency, to_currency, rate)
        return tb

    def _apply_consolidation_method(self, tb: Dict[str, Any], ownership: Decimal, method: str) -> Dict[str, Any]:
        multiplier = Decimal('1.0')

        if method == HoldingMembership.ConsolidationMethod.PROPORTIONAL:
            multiplier = ownership / Decimal('100.0')
        elif method == HoldingMembership.ConsolidationMethod.EQUITY:
            # EQUITY: Solo se aplica a cuentas de resultado (Ingresos 4, Gastos 5)
            for line in tb['lines']:
                if not line['account_code'].startswith(('4', '5')):
                    line['debit'] = Decimal('0')
                    line['credit'] = Decimal('0')
                    line['balance'] = Decimal('0')
                else:
                    line['debit'] *= (ownership / Decimal('100.0'))
                    line['credit'] *= (ownership / Decimal('100.0'))
                    line['balance'] *= (ownership / Decimal('100.0'))
            return tb

        # FULL o PROPORTIONAL (lineal)
        if multiplier != Decimal('1.0'):
            for line in tb['lines']:
                line['debit'] *= multiplier
                line['credit'] *= multiplier
                line['balance'] *= multiplier

        return tb

    def _aggregate_balances(self, individual_balances: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        aggregated: Dict[str, Dict[str, Any]] = {}

        for tb in individual_balances:
            for line in tb['lines']:
                code = line['account_code']
                if code not in aggregated:
                    aggregated[code] = {
                        'account_code': code,
                        'account_name': line['account_name'],
                        'debit': Decimal('0'),
                        'credit': Decimal('0'),
                        'balance': Decimal('0'),
                        'is_eliminated': False
                    }
                aggregated[code]['debit'] += line['debit']
                aggregated[code]['credit'] += line['credit']
                aggregated[code]['balance'] += line['balance']

        return aggregated

    def _build_trial_balance_report(self, holding: HoldingEntity, data: Dict[str, Any], cutoff_date: Any) -> Dict[str, Any]:
        return {
            'holding_id': str(holding.id),
            'holding_name': holding.name,
            'base_currency': holding.base_currency,
            'cutoff_date': str(cutoff_date),
            'accounts': list(data.values()),
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'status': 'final'
            }
        }
