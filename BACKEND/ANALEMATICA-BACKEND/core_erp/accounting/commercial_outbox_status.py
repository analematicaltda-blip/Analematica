"""Read-only transport counts. Never treats an outbox flag as fiscal acceptance."""
from uuid import UUID
from django.db.models import Count
from apps.core_erp.tenancy.models import Tenant
from apps.core_erp.outbox_models import OutboxEvent
from .exceptions import AccountingError

EVENTS = {'commercial.invoice.requested.v1': 'invoice_requests',
          'operations.reservation.confirmed.v1': 'reservation_confirmations'}


def inspect_commercial_outbox(company_id):
    company = str(UUID(str(company_id)))
    if not Tenant.objects.filter(pk=company, is_active=True, state='ACTIVE').exists():
        raise AccountingError('Active company required.')
    counts = {name: {'PENDING': 0, 'PROCESSED': 0, 'ERROR': 0, 'OTHER': 0} for name in EVENTS.values()}
    grouped = (OutboxEvent.objects.filter(payload__company_id=company, event_type__in=EVENTS)
               .values('event_type', 'status').annotate(total=Count('pk')))
    for row in grouped:
        status = row['status'] if row['status'] in {'PENDING', 'PROCESSED', 'ERROR'} else 'OTHER'
        counts[EVENTS[row['event_type']]][status] += row['total']
    return {'company_id': company, 'read_only': True, 'transport_counts': counts,
            'fiscal_consumer_available': False, 'fiscal_receipt_verified': False,
            'fiscal_acceptance': 'NOT_VERIFIED', 'blocking_reason': 'FISCAL_CONSUMER_NOT_INTEGRATED',
            'outbox_status_is_fiscal_acceptance': False, 'financial_values_omitted': True,
            'published_by_this_call': False, 'ledger_written': False}
