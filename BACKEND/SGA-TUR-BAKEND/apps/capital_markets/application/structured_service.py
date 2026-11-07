import logging
import uuid
from decimal import Decimal
from django.utils import timezone
from ..domain.models import MarketRating, StructuredDeal

logger = logging.getLogger(__name__)

class RatingSimulationService:
    """
    Rating & Market Perception Engine (Phase 16).
    Simulates credit rating changes based on capital structure.
    """

    @staticmethod
    def simulate_rating(tenant_id, debt_ratio):
        """
        Determines credit rating score.
        """
        rating_score = 'AA'
        if debt_ratio > 0.4: rating_score = 'A'
        if debt_ratio > 0.6: rating_score = 'BBB'
        if debt_ratio > 0.8: rating_score = 'JUNK'

        rating = MarketRating.objects.create(
            tenant_id=tenant_id,
            agency_source="INTERNAL_SIM",
            rating_score=rating_score,
            default_probability=Decimal('0.0200'),
            market_spread_bps=250
        )

        logger.info(f"Rating Engine: Internal rating for {tenant_id} is {rating_score}")
        return rating

class StructuredFinanceService:
    """
    Structured Finance Module (Phase 16).
    Handles asset securitization and SPV management.
    """

    @staticmethod
    def structure_abs(tenant_id, asset_type, total_size):
        """
        Structures an Asset-Backed Security deal.
        """
        deal = StructuredDeal.objects.create(
            tenant_id=tenant_id,
            deal_name=f"ABS-{asset_type}-{timezone.now().year}",
            underlying_asset_type=asset_type,
            total_size=total_size,
            tranche_structure={
                "Senior": "70%",
                "Mezzanine": "20%",
                "Equity": "10%"
            },
            spv_legal_name=f"Sarita Global SPV-{uuid.uuid4().hex[:6]}"
        )

        logger.info(f"Structured Finance: New deal structured - {deal.deal_name}")
        return deal
