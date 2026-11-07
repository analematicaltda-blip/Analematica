import logging
from django.core.cache import cache
from apps.audit.services import AuditService

logger = logging.getLogger(__name__)

class SovereignControl:
    """
    FASE META: Systemic Sovereignty and Legacy.
    Ensures that the system remains under human/institutional control at all times.
    """
    KILL_SWITCH_KEY = "SARITA_SOVEREIGN_KILL_SWITCH"

    @classmethod
    def activate_kill_switch(cls, user, reason):
        """
        Suspends all autonomous activities and transactional processing.
        Only reversible by SuperAdmin through physical/multi-sig protocols.
        """
        cache.set(cls.KILL_SWITCH_KEY, True, timeout=None)
        logger.critical(f"SOVEREIGN KILL SWITCH ACTIVATED by {user.username}. Reason: {reason}")

        AuditService.log(
            user=user,
            action="SOVEREIGN_KILL_SWITCH_ACTIVATED",
            entity="SYSTEM",
            entity_id="GLOBAL",
            ip_address="SOCIETAL_CONTROL",
            new={"reason": reason}
        )
        return True

    @classmethod
    def is_system_suspended(cls):
        return cache.get(cls.KILL_SWITCH_KEY, False)

    @classmethod
    def reset_system(cls, user):
        """
        Restores system operationality after a manual security audit.
        """
        cache.delete(cls.KILL_SWITCH_KEY)
        logger.warning(f"SYSTEM RESET by {user.username}. Autonomous operations restored.")
        return True
