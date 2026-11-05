from decimal import Decimal
from .models import HoldingRegion, TaxRule

class TaxComplianceEngine:
    """
    Motor modular de cumplimiento fiscal (Fase 6).
    """

    @staticmethod
    def calculate_taxes(base_amount, country_code):
        region = HoldingRegion.objects.filter(country_code=country_code).first()
        if not region:
            return []

        tax_impact = []
        total_tax_amount = Decimal('0.00')

        rules = region.tax_rules.filter(is_active=True)
        for rule in rules:
            amount = base_amount * (rule.percentage / 100)
            total_tax_amount += amount
            tax_impact.append({
                "tax_name": rule.name,
                "percentage": float(rule.percentage),
                "amount": amount
            })

        return {
            "base_amount": base_amount,
            "tax_details": tax_impact,
            "total_tax": total_tax_amount,
            "grand_total": base_amount + total_tax_amount
        }

    @staticmethod
    def generate_local_tax_report(country_code, period_start, period_end):
        """
        Genera el rastro necesario para declaraciones locales.
        """
        # Aquí se filtrarían transacciones ERP por perfil_ref_id asociado a la región
        return {
            "jurisdiction": country_code,
            "status": "READY_FOR_EXPORT",
            "message": f"Reporte fiscal generado para {country_code}."
        }
