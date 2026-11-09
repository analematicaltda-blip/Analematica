"""Trusted application context is injected by the authenticated caller, not command metadata."""
from typing import Dict, Any
from .domain_contracts.base import IApplicationService, DomainCommand, CreateReservationCommand, ConfirmReservationCommand

class ReservationApplicationService(IApplicationService):
    def __init__(self, *, actor=None, provider_id=None):
        self.actor = actor
        self.provider_id = provider_id

    def execute(self, command: DomainCommand) -> Dict[str, Any]:
        if isinstance(command, CreateReservationCommand):
            # The legacy creation method is absent; never fabricate an identifier.
            return {'success': False, 'error_code': 'RESERVATION_CREATION_NOT_INTEGRATED'}
        if not isinstance(command, ConfirmReservationCommand):
            return {'success': False, 'error_code': 'UNSUPPORTED_COMMAND'}
        if self.actor is None or self.provider_id is None:
            return {'success': False, 'error_code': 'AUTHENTICATED_CONTEXT_REQUIRED'}
        from apps.domain_business.operativa.sargentos import DomainSargentoReservas
        from apps.core_erp.accounting.exceptions import AccountingError
        from rest_framework.exceptions import APIException
        from django.core.exceptions import ValidationError
        try:
            result = DomainSargentoReservas.confirm_reservation(
                command.reserva_id, actor=self.actor, provider_id=self.provider_id)
        except (AccountingError, APIException, ValidationError, ValueError):
            return {'success': False, 'error_code': 'RESERVATION_CONFIRMATION_REJECTED'}
        return {'success': True, **result}
