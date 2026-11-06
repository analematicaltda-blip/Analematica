import logging
from decimal import Decimal
from django.utils import timezone
from django.db import models
from ..models import Tax, TaxRate, TaxRule, TaxTransaction
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class TaxCalculatorEngine:
    """
    Motor de Cumplimiento Fiscal Parametrizable (Fase 6.2).
    Evalúa dinámicamente reglas de impuestos basadas en jurisdicción y contexto.
    """

    @staticmethod
    def calculate_taxes(tenant_id: str, document_type: str, entity_type: str, base_amount: Decimal, jurisdiction_id=None):
        """
        Evalúa y calcula todos los impuestos aplicables a una transacción.
        """
        query = {
            "tenant_id": tenant_id,
            "active": True,
            "effective_from__lte": timezone.now().date()
        }
        if jurisdiction_id:
            query["jurisdiction_id"] = jurisdiction_id

        applicable_taxes = Tax.objects.filter(**query)
        results = []

        for tax in applicable_taxes:
            # Evaluar reglas específicas
            rule = TaxRule.objects.filter(
                tax=tax,
                document_type=document_type,
                entity_type=entity_type,
                minimum_base__lte=base_amount
            ).filter(
                models.Q(maximum_base__gte=base_amount) | models.Q(maximum_base__isnull=True)
            ).order_by('-priority').first()

            if rule:
                # Obtener tasa vigente
                rate_obj = tax.rates.filter(
                    effective_from__lte=timezone.now().date()
                ).filter(
                    models.Q(effective_to__gte=timezone.now().date()) | models.Q(effective_to__isnull=True)
                ).order_by('-effective_from').first()

                if rate_obj:
                    tax_amount = (base_amount * rate_obj.rate).quantize(Decimal('1.00'))
                    results.append({
                        "tax_id": str(tax.id),
                        "tax_name": tax.name,
                        "tax_code": tax.code,
                        "base_amount": float(base_amount),
                        "tax_amount": float(tax_amount),
                        "rate": float(rate_obj.rate),
                        "type": tax.tax_type
                    })

        return results

    @staticmethod
    def record_tax_transaction(tenant_id: str, document_id: str, tax_data: list):
        """
        Persiste el impacto fiscal y emite eventos auditables.
        """
        for item in tax_data:
            tax = Tax.objects.get(id=item["tax_id"])
            tx = TaxTransaction.objects.create(
                tenant_id=tenant_id,
                document_id=document_id,
                tax=tax,
                base_amount=Decimal(str(item["base_amount"])),
                tax_amount=Decimal(str(item["tax_amount"])),
                rate_applied=Decimal(str(item["rate"]))
            )

            # Emitir evento para Torre de Control
            EventBus.emit("TAX_TRANSACTION_RECORDED", {
                "tenant_id": tenant_id,
                "tax_code": tax.code,
                "amount": item["tax_amount"],
                "document_id": str(document_id)
            })

        return True
