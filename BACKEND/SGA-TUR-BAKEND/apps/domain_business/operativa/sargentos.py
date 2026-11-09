"""Reservation transitions scoped to an independently verified business owner."""
from uuid import UUID, uuid5
from django.db import transaction
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.core_erp.accounting.validation import current_actor, lock_company
from apps.turismo.models import TourismProvider, VerifiedCompanyLink
from apps.turismo.services.company_identity import resolve_company
from .models import Reservation


RESERVATION_EVENT = 'operations.reservation.confirmed.v1'
RESERVATION_NAMESPACE = UUID('b7b1db27-814b-4d2b-9afc-84daac0d6d31')


class DomainSargentoReservas:
    @staticmethod
    @transaction.atomic
    def confirm_reservation(reservation_id, *, actor=None, provider_id=None):
        if actor is None or provider_id is None:
            raise PermissionDenied('Se requiere contexto empresarial autenticado.')
        user = current_actor(actor)
        initial = resolve_company(user, provider_id)
        lock_company(initial.tenant_id)
        # Serialize with link revocation and ownership changes, then revalidate.
        VerifiedCompanyLink.objects.select_for_update().get(pk=initial.pk)
        TourismProvider.objects.select_for_update().get(pk=provider_id)
        link = resolve_company(user, provider_id)
        if link.tenant_id != initial.tenant_id:
            raise PermissionDenied('El vínculo empresarial cambió.')
        reservation = Reservation.plain_objects.select_for_update().filter(
            pk=reservation_id, tenant_id=link.tenant_id).first()
        if reservation is None:
            raise PermissionDenied('Reserva no disponible en esta empresa.')
        replayed = reservation.status == Reservation.Status.CONFIRMED
        if reservation.status not in {Reservation.Status.PENDING, Reservation.Status.CONFIRMED}:
            raise ValidationError('El estado actual no permite confirmar la reserva.')
        event_id = uuid5(RESERVATION_NAMESPACE, str(reservation.pk))
        payload = {'schema': 'sgacd-reservation-confirmed-v1', 'company_id': str(link.tenant_id),
                   'provider_id': str(provider_id), 'reservation_id': str(reservation.pk),
                   'actor_id': str(user.pk), 'from_status': 'PENDING', 'to_status': 'CONFIRMED',
                   'source_model': 'domain_business.Reservation', 'fiscal_ready': False}
        event = OutboxEvent.objects.filter(pk=event_id).first()
        if event is not None and (event.event_type != RESERVATION_EVENT or event.domain != 'operations'
                or event.aggregate_root != str(reservation.pk) or event.version != 1 or event.payload != payload):
            raise ValidationError('El evento de confirmación presenta un conflicto de integridad.')
        if not replayed and event is not None:
            raise ValidationError('Existe un evento sin transición coherente; requiere revisión.')
        if not replayed:
            reservation.status = Reservation.Status.CONFIRMED
            reservation.save(update_fields=['status', 'updated_at'])
            event = OutboxEvent.objects.create(id=event_id, event_type=RESERVATION_EVENT, domain='operations',
                                               aggregate_root=str(reservation.pk), payload=payload, version=1)
        return {'reservation_id': str(reservation.pk), 'status': reservation.status,
                'replayed': replayed, 'confirmation_event_recorded': event is not None,
                'confirmation_event_id': str(event_id) if event is not None else None,
                'published_by_this_call': False, 'ledger_written': False, 'fiscal_accepted': False}
