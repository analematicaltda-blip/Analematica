import logging
from .models import TransferPricingRule, LegalEntity, IntercompanyTransaction
from .intercompany_engine import IntercompanyEngine
from decimal import Decimal

logger = logging.getLogger(__name__)

class TransferPricingEngine:
    """
    Automates the application of transfer pricing rules (IP royalties, markups).
    """

    @staticmethod
    def apply_ip_royalty(opco_id, ipco_id, base_revenue):
        """
        Calculates and bills royalty from OpCo to IP Co.
        """
        try:
            rule = TransferPricingRule.objects.get(
                source_type='OPERATING',
                dest_type='IP_CO',
                is_active=True
            )

            royalty_amount = base_revenue * (rule.markup_percentage / 100)

            return IntercompanyEngine.create_intercompany_billing(
                source_id=opco_id,
                dest_id=ipco_id,
                amount=royalty_amount,
                description=f"IP Royalty Payment based on revenue {base_revenue}",
                tx_type='ROYALTY'
            )
        except TransferPricingRule.DoesNotExist:
            logger.warning("No IP Royalty rule found.")
            return None

    @staticmethod
    def apply_infra_markup(opco_id, infraco_id, cost_basis):
        """
        Bills infrastructure service with markup from Infra Co to OpCo.
        """
        try:
            rule = TransferPricingRule.objects.get(
                source_type='INFRA_CO',
                dest_type='OPERATING',
                is_active=True
            )

            total_bill = cost_basis * (1 + (rule.markup_percentage / 100))

            # Note: Source is who BILLS, Destination is who PAYS.
            # In our IntercompanyEngine logic, source is the one receiving money (Receivable)
            return IntercompanyEngine.create_intercompany_billing(
                source_id=infraco_id,
                dest_id=opco_id,
                amount=total_bill,
                description=f"Infrastructure Service Billing with {rule.markup_percentage}% markup",
                tx_type='BILLING'
            )
        except TransferPricingRule.DoesNotExist:
            return None
