import logging
import hashlib
from django.db import transaction
from ..models import DigitalIdentity

logger = logging.getLogger(__name__)

class IdentityTrustService:
    """
    Identity & Trust Framework - Phase 23.5.
    Gestiona identidad digital institucional, certificados y validación KYB.
    """

    @staticmethod
    def register_digital_identity(entity_name, metadata):
        """
        Registra una nueva identidad digital descentralizada (DID) para una entidad del holding.
        """
        did = f"did:sarita:{hashlib.sha256(entity_name.encode()).hexdigest()[:16]}"
        cert_hash = hashlib.sha256(str(metadata).encode()).hexdigest()

        identity = DigitalIdentity.objects.create(
            entity_name=entity_name,
            identity_did=did,
            certificate_hash=cert_hash,
            permission_grid=metadata.get('permissions', {})
        )

        logger.info(f"Trust Framework: Registered ID for {entity_name} -> {did}")
        return identity

    @staticmethod
    @transaction.atomic
    def verify_kyb(identity_id):
        """
        Realiza la validación Know Your Business (KYB) institucional.
        """
        identity = DigitalIdentity.objects.get(id=identity_id)
        # Simulation: Remote validation against sovereign registries (Phase 21)
        identity.is_kyb_verified = True
        identity.save()

        logger.info(f"Trust Framework: KYB Verified for {identity.entity_name}")
        return True

    @staticmethod
    def validate_permission(did, action_requested):
        """
        Valida si una identidad digital tiene permiso para realizar una acción específica.
        """
        identity = DigitalIdentity.objects.filter(identity_did=did, is_kyb_verified=True).first()
        if identity:
            permissions = identity.permission_grid
            return permissions.get(action_requested, False)

        return False
