import logging
import hashlib
from django.utils import timezone
from django.db import transaction
from ..domain.models import TokenizedAsset, ProgrammableCapitalUnit, DigitalRegistry
from .compliance_service import ComplianceFilterService

logger = logging.getLogger(__name__)

class SecondaryLiquidityService:
    """
    Secondary Market Layer (Phase 17).
    Manages controlled transfers between verified investors.
    """

    @staticmethod
    @transaction.atomic
    def execute_transfer(tenant_id, unit_id, from_holder_id, to_holder_id):
        """
        Transfers a programmable unit from one holder to another.
        """
        unit = ProgrammableCapitalUnit.objects.select_for_update().get(unit_id=unit_id)
        asset = unit.asset

        # 1. Compliance Validation
        ComplianceFilterService.validate_transfer(asset, from_holder_id, to_holder_id, 1)

        # 2. Ownership Update
        unit.current_holder_id = to_holder_id
        unit.save()

        # 3. Registry Update (Inmutable Audit)
        tx_hash = hashlib.sha256(f"TRANSFER-{unit_id}-{timezone.now().timestamp()}".encode()).hexdigest()
        DigitalRegistry.objects.create(
            tenant_id=tenant_id,
            asset=asset,
            unit=unit,
            from_holder_id=from_holder_id,
            to_holder_id=to_holder_id,
            quantity=1, # Single unit transfer
            transaction_hash=tx_hash
        )

        logger.info(f"Liquidity: Unit {unit_id} transferred to {to_holder_id}. Hash: {tx_hash[:16]}")
        return tx_hash
