import logging
from decimal import Decimal
from django.db import transaction
from ..models import MetaLiquidityPool, MetaEcosystem

logger = logging.getLogger(__name__)

class MetaLiquidityService:
    """
    Meta-Liquidity Grid - Phase 20.5.
    Gestiona pooling dinámico de capital y buffers de estabilización entre ecosistemas.
    """

    @staticmethod
    @transaction.atomic
    def activate_emergency_pooling(pool_id):
        """
        Activa el pooling de emergencia para inyectar liquidez en ecosistemas en crisis.
        """
        pool = MetaLiquidityPool.objects.get(id=pool_id)
        pool.is_emergency_active = True

        # Mobilize stabilization buffer
        if pool.stabilization_buffer > 0:
            injection_per_eco = pool.stabilization_buffer / Decimal(str(pool.participating_ecosystems.count()))

            for eco in pool.participating_ecosystems.all():
                eco.liquidity_depth += injection_per_eco
                eco.save()
                logger.warning(f"Meta-Liquidity: Injected {injection_per_eco} from Buffer to {eco.name}")

            pool.stabilization_buffer = Decimal('0')
            pool.save()

        return True

    @staticmethod
    @transaction.atomic
    def rebalance_pool(pool_id):
        """
        Balancea la liquidez total del pool entre sus participantes basado en su output económico.
        """
        pool = MetaLiquidityPool.objects.get(id=pool_id)
        participants = pool.participating_ecosystems.all()
        total_output = sum(p.economic_output for p in participants)

        if total_output > 0:
            for eco in participants:
                share = eco.economic_output / total_output
                eco.liquidity_depth = pool.total_liquidity * share
                eco.save()

        logger.info(f"Meta-Liquidity: Rebalanced Pool {pool.name}")
        return True
