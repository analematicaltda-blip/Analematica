import logging
from typing import Dict, Any, Type
from .domain_contracts.base import DomainCommand, IApplicationService

logger = logging.getLogger(__name__)

class ApplicationServiceRegistry:
    """
    Registry for Application Services to avoid static cross-imports.
    """
    _services: Dict[str, IApplicationService] = {}

    @classmethod
    def register(cls, command_type: Type[DomainCommand], service: IApplicationService):
        cls._services[command_type.__name__] = service
        logger.info(f"Service registered for command: {command_type.__name__}")

    @classmethod
    def get_service(cls, command: DomainCommand) -> IApplicationService:
        service = cls._services.get(type(command).__name__)
        if not service:
            # Fallback for Phase 1: dynamic discovery or generic service
            from .reservation_service import ReservationApplicationService
            return ReservationApplicationService()
        return service

    @classmethod
    def dispatch(cls, command: DomainCommand) -> Dict[str, Any]:
        service = cls.get_service(command)
        return service.execute(command)
