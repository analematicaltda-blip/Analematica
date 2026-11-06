from decimal import Decimal
import logging
from django.db.models import Q
from apps.core_erp.taxation.models import Tax, TaxRate, TaxRule, TaxTransaction

logger = logging.getLogger(__name__)

class TaxOrchestrator:
    """
    Hallazgo 16: Motor Fiscal Inteligente Expandido.
    Coordina cálculos de IVA, ReteFuente y ReteICA basados en territorialidad.
    """

    @staticmethod
    def calculate_all_taxes(tenant_id, document_type, entity_type, amount, city_id=None):
        """
        Orquesta el cálculo de todos los impuestos aplicables.
        """
        base_amount = Decimal(str(amount))

        # 1. Calcular IVA
        iva = TaxOrchestrator._calculate_specific_tax(tenant_id, 'IVA', document_type, entity_type, base_amount)

        # 2. Calcular ReteFuente
        rete_fuente = TaxOrchestrator._calculate_specific_tax(tenant_id, 'RETEFUENTE', document_type, entity_type, base_amount)

        # 3. Calcular ReteICA (Requiere Ciudad/Municipio)
        rete_ica = 0
        if city_id:
            rete_ica = TaxOrchestrator._calculate_specific_tax(tenant_id, 'RETEICA', document_type, entity_type, base_amount, city_id)

        total_taxes = iva + rete_fuente + rete_ica

        return {
            "base_amount": float(base_amount),
            "iva": float(iva),
            "rete_fuente": float(rete_fuente),
            "rete_ica": float(rete_ica),
            "total_taxes": float(total_taxes),
            "net_amount": float(base_amount + iva - rete_fuente - rete_ica)
        }

    @staticmethod
    def _calculate_specific_tax(tenant_id, tax_type, document_type, entity_type, base_amount, jurisdiction_id=None):
        query = Q(tenant_id=tenant_id, tax_type=tax_type, active=True)
        if jurisdiction_id:
            query &= Q(jurisdiction_id=jurisdiction_id)

        tax = Tax.objects.filter(query).first()
        if not tax:
            return Decimal('0.00')

        # Evaluar Regla
        rule = TaxRule.objects.filter(
            tax=tax,
            document_type=document_type,
            entity_type=entity_type,
            minimum_base__lte=base_amount
        ).filter(Q(maximum_base__gte=base_amount) | Q(maximum_base__isnull=True)).first()

        if not rule:
            return Decimal('0.00')

        # Obtener Tasa
        rate_obj = TaxRate.objects.filter(tax=tax).order_by('-effective_from').first()
        if not rate_obj:
            return Decimal('0.00')

        return (base_amount * rate_obj.rate).quantize(Decimal('1.00'))
