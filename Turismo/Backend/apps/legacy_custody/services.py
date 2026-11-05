import logging
import json
from typing import Dict, Any, List
from .models import LegacyCustodian, LegacyMilestone

logger = logging.getLogger(__name__)

class LegacyCustodyService:
    """
    Servicio encargado de la preservación y transmisión del conocimiento civilizatorio de SARITA.
    """

    def __init__(self, authorized_user):
        self.user = authorized_user

    def generate_legacy_bundle(self) -> Dict[str, Any]:
        """
        Genera un paquete de evidencia inmutable del estado del sistema, sus principios y su gobernanza.
        """
        from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
        kernel = GovernanceKernel(self.user)

        bundle = {
            "version": "1.0.0-LEGADO",
            "system_standard": kernel.get_meta_standard_metadata(),
            "custodians": list(LegacyCustodian.objects.filter(is_active=True).values('name', 'entity_represented', 'role')),
            "historical_milestones": list(LegacyMilestone.objects.order_by('-timestamp').values('title', 'timestamp', 'governance_hash')[:10]),
            "protection_status": "LOCKED_FOR_CIVILIZATION",
            "integrity_signature": "SARITA_NON_REPUDIATION_MASTER_KEY"
        }

        logger.info(f"LEGADO: Paquete de transmisión generado por {self.user.username}")
        return bundle

    def appoint_custodian(self, name: str, entity: str, public_key: str):
        """
        Nombra un nuevo garante del sistema. Requiere autoridad soberana.
        """
        if not self.user.is_superuser:
            raise PermissionError("Solo la Autoridad Soberana puede nombrar custodios del legado.")

        custodian = LegacyCustodian.objects.create(
            name=name,
            entity_represented=entity,
            public_key=public_key
        )
        logger.warning(f"LEGADO: Nuevo custodio nombrado: {name} ({entity})")
        return custodian
