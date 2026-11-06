import logging
from decimal import Decimal
from django.db.models import Sum
from ..models import Shareholder, ShareClass, ShareIssuance, EquityRound

logger = logging.getLogger(__name__)

class CapitalStructureEngine:
    """
    Motor de Estructura de Capital y Cascada de Liquidación (Fase 8).
    Calcula dilución, valoraciones post-money y cascadas de salida.
    """

    @staticmethod
    def calculate_current_ownership():
        """
        Calcula el porcentaje de propiedad actual por accionista (Fully Diluted).
        """
        total_shares = ShareIssuance.objects.aggregate(total=Sum('shares_count'))['total'] or 0
        if total_shares == 0:
            return []

        ownership = []
        shareholders = Shareholder.objects.all()

        for holder in shareholders:
            holder_shares = holder.issuances.aggregate(total=Sum('shares_count'))['total'] or 0
            if holder_shares > 0:
                ownership.append({
                    "shareholder": holder.name,
                    "type": holder.type,
                    "shares": holder_shares,
                    "percentage": (Decimal(str(holder_shares)) / Decimal(str(total_shares))) * 100
                })

        return sorted(ownership, key=lambda x: x['percentage'], reverse=True)

    @staticmethod
    def simulate_new_round(pre_money_val, investment_amount):
        """
        Simula una nueva ronda de inversión y calcula la dilución resultante.
        """
        post_money_val = pre_money_val + investment_amount
        new_investor_stake = (investment_amount / post_money_val) * 100
        dilution_factor = Decimal('1') - (investment_amount / post_money_val)

        current_ownership = CapitalStructureEngine.calculate_current_ownership()
        simulated_ownership = []

        for entry in current_ownership:
            simulated_ownership.append({
                "shareholder": entry['shareholder'],
                "old_percentage": entry['percentage'],
                "new_percentage": entry['percentage'] * dilution_factor
            })

        simulated_ownership.append({
            "shareholder": "Nuevo Inversor (Ronda Sim)",
            "old_percentage": 0,
            "new_percentage": new_investor_stake
        })

        return {
            "pre_money": pre_money_val,
            "investment": investment_amount,
            "post_money": post_money_val,
            "new_ownership_table": simulated_ownership
        }

    @staticmethod
    def calculate_liquidation_waterfall(exit_value):
        """
        Análisis Waterfall: Distribución de proceeds en una salida.
        Considera preferencias de liquidación de acciones preferentes.
        """
        remaining_proceeds = exit_value
        distributions = {}

        # 1. Pago de Preferencias (Liquidation Preference)
        # Obtenemos emisiones de clases preferentes
        preferred_issuances = ShareIssuance.objects.filter(share_class__type=ShareClass.Type.PREFERRED)

        for issuance in preferred_issuances:
            pref_multiple = issuance.share_class.liquidation_preference
            invested_amount = issuance.shares_count * issuance.price_per_share
            preference_payout = min(remaining_proceeds, invested_amount * pref_multiple)

            distributions[issuance.shareholder.name] = distributions.get(issuance.shareholder.name, Decimal('0')) + preference_payout
            remaining_proceeds -= preference_payout

            if remaining_proceeds <= 0:
                break

        # 2. Distribución Pro-Rata del remanente (Acciones comunes + Participantes)
        if remaining_proceeds > 0:
            ownership = CapitalStructureEngine.calculate_current_ownership()
            for entry in ownership:
                share_val = (entry['percentage'] / 100) * remaining_proceeds
                distributions[entry['shareholder']] = distributions.get(entry['shareholder'], Decimal('0')) + share_val

        return {
            "exit_value": exit_value,
            "distributions": distributions,
            "breakdown": [{"shareholder": k, "amount": v} for k, v in distributions.items()]
        }
