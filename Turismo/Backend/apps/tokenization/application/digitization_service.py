import logging
import hashlib
import uuid
from decimal import Decimal
from django.utils import timezone
from ..domain.models import TokenizedAsset, DigitalRegistry, ProgrammableCapitalUnit
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class AssetDigitizationService:
    """
    Asset Digitization Engine (Phase 17).
    Converts traditional assets into programmable digital representations.
    """

    @staticmethod
    def digitize_equity(tenant_id, name, underlying_asset_id, jurisdiction, total_supply, par_value):
        """
        Creates a digital equity token for an underlying entity or project.
        """
        asset = TokenizedAsset.objects.create(
            tenant_id=tenant_id,
            name=name,
            asset_type=TokenizedAsset.AssetType.EQUITY,
            classification=TokenizedAsset.RegulatoryClassification.SECURITY,
            underlying_asset_ref_id=underlying_asset_id,
            jurisdiction=jurisdiction,
            total_supply=total_supply,
            par_value=par_value,
            valuation_model="NAV_BASED"
        )

        # 1. Initial Minting Record in Digital Registry
        tx_hash = hashlib.sha256(f"MINT-{asset.id}-{timezone.now().timestamp()}".encode()).hexdigest()
        DigitalRegistry.objects.create(
            tenant_id=tenant_id,
            asset=asset,
            from_holder_id=None,
            to_holder_id=tenant_id, # Initial ownership by holding
            quantity=total_supply,
            transaction_hash=tx_hash,
            metadata={"reason": "Initial Digitization"}
        )

        logger.info(f"Tokenization: Asset '{name}' digitized successfully. Hash: {tx_hash[:16]}")

        EventBus.emit("ASSET_DIGITIZED", {
            "tenant_id": str(tenant_id),
            "asset_id": str(asset.id),
            "asset_type": "EQUITY",
            "total_supply": str(total_supply)
        })

        return asset

    @staticmethod
    def fractionate_asset(tenant_id, asset_id, num_units):
        """
        Breaks down a tokenized asset into programmable units.
        """
        asset = TokenizedAsset.objects.get(id=asset_id)
        unit_percentage = Decimal('100.0') / Decimal(str(num_units))

        units = []
        for i in range(num_units):
            unit = ProgrammableCapitalUnit.objects.create(
                tenant_id=tenant_id,
                asset=asset,
                unit_id=f"{asset.name[:3].upper()}-{uuid.uuid4().hex[:6]}",
                ownership_percentage=unit_percentage,
                current_holder_id=tenant_id
            )
            units.append(unit)

        logger.info(f"Tokenization: Asset {asset_id} fractionated into {num_units} units.")
        return units
