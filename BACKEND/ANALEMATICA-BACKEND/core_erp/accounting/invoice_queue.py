"""Internal transactional invoice-request outbox; no fiscal emission or publication.
Authorization and authoritative source locking belong to the calling producer.
"""
import re
from uuid import UUID, uuid5
from django.db import transaction
from ..outbox_models import OutboxEvent
from .invoice_intent import prepare_invoice_intent
from .validation import lock_company, current_actor

EVENT_TYPE = 'commercial.invoice.requested.v1'
NAMESPACE = UUID('5694db02-a1ba-4a64-a19f-41fbe1912a21')


@transaction.atomic
def enqueue_invoice_intent(snapshot, *, company_id, actor, source_review=None):
    """Persist once inside caller transaction; caller must authorize and lock source.

    No network calls or on_commit publisher. The outbox records a request only;
    it cannot stand in for a fiscal receipt, invoice, payment or ledger posting.
    """
    company = lock_company(company_id)
    user = current_actor(actor)
    intent = prepare_invoice_intent(snapshot, str(company.pk))
    identifier = uuid5(NAMESPACE, intent['idempotency_key'])
    payload = {'schema': 'sgacd-invoice-outbox-v1', 'company_id': str(company.pk),
               'requested_by': str(user.pk), 'intent': intent}
    if source_review is not None:
        keys={'review_id','intent_digest','source_fingerprint','evidence_digest'}
        if not isinstance(source_review,dict) or set(source_review)!=keys:
            raise ValueError('Unsupported source review reference.')
        if not isinstance(source_review['review_id'],str) or str(UUID(source_review['review_id']))!=source_review['review_id']:
            raise ValueError('Canonical review UUID required.')
        if any(not isinstance(source_review[key],str) or not re.fullmatch('[0-9a-f]{64}',source_review[key]) for key in keys-{'review_id'}):
            raise ValueError('Source evidence digests required.')
        if source_review['intent_digest']!=intent['payload_digest']:
            raise ValueError('Source review does not match invoice intent.')
        payload['source_review']=dict(source_review)
    existing = OutboxEvent.objects.filter(pk=identifier).first()
    if existing is not None:
        if (existing.event_type != EVENT_TYPE or existing.domain != 'commercial'
                or existing.aggregate_root != snapshot['source_id'] or existing.version != 1
                or existing.payload != payload):
            raise ValueError('Invoice request identity conflicts with persisted content.')
        return {'outbox_id': str(identifier), 'replayed': True, 'request_persisted': True, 'outbox_status': existing.status,
                'published_by_this_call': False, 'fiscal_accepted': False, 'ledger_written': False}
    OutboxEvent.objects.create(id=identifier, event_type=EVENT_TYPE, domain='commercial',
                              aggregate_root=snapshot['source_id'], payload=payload, version=1)
    return {'outbox_id': str(identifier), 'replayed': False, 'request_persisted': True, 'outbox_status': 'PENDING',
            'published_by_this_call': False, 'fiscal_accepted': False, 'ledger_written': False}
