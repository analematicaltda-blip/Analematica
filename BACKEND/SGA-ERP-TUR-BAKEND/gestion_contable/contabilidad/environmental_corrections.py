"""Append-only owner-reviewed corrections of recorded environmental observations.

Original activity claims and factors remain intact. Revisions replace the effective
estimate, never add a second emission for the same observed activity. No offsets,
liabilities, certification, payments, or source authenticity are inferred.
"""
import re
from uuid import UUID
from django.db import transaction
from django.utils import timezone
from apps.core_erp.accounting.environmental import estimate
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from . import environmental_records as records
from .tourism_metrics import _context

REVIEW = 'accounting.environmental.correction-reviewed.v1'
CORRECTED = 'accounting.environmental.corrected.v1'
REASONS = {'QUANTITY_ERROR', 'FACTOR_VERSION', 'ALLOCATION_ERROR', 'DATA_CORRECTION'}
MAX_REVISIONS = 100

def _root(company, provider, observation_id):
    record = OutboxEvent.objects.using('default').filter(pk=UUID(str(observation_id)),
        event_type=records.RECORDED, payload__company_id=str(company.pk),
        payload__provider_id=str(provider.pk)).first()
    if record is None:
        raise AccountingError('Recorded scoped observation required.')
    review, body = records._review(company, provider, record.payload.get('review_id'))
    records._verify_record(company, provider, record, review, body)
    return record, body['assessment']

def _validate_assessment(company, original, assessment):
    if not isinstance(assessment, dict) or not isinstance(assessment.get('snapshot'), dict):
        raise AccountingError('Correction assessment required.')
    snapshot = assessment['snapshot']
    if snapshot.get('company_id') != str(company.pk) or estimate(company_id=company.pk,
            activities=snapshot.get('activities'), factors=snapshot.get('factors')) != assessment:
        raise AccountingError('Correction no longer matches its explicit sources.')
    # Corrections may change values, not reclaim another activity or shift its date/unit.
    identity = lambda value: sorted((a['id'], a['date'], a['unit'], a.get('source_reference'), a.get('source_segment')) for a in value['snapshot']['activities'])
    if identity(original) != identity(assessment):
        raise AccountingError('Activity identities, economic dates and units must be preserved.')
    if any(a['date'] > timezone.localdate().isoformat() for a in snapshot['activities']):
        raise AccountingError('Future activity cannot be corrected as an observation.')

def _review(company, provider, review_id, original, observation_id):
    row = OutboxEvent.objects.using('default').filter(pk=UUID(str(review_id)), event_type=REVIEW).first()
    payload = row.payload if row else None
    if not isinstance(payload, dict) or set(payload) != {'company_id','provider_id','review','review_digest'}:
        raise AccountingError('Correction review unavailable.')
    body = payload['review']
    fields = {'observation_id','revision','previous_digest','assessment','reason_code','evidence_digest','reviewed_by'}
    if (payload['company_id'] != str(company.pk) or payload['provider_id'] != str(provider.pk)
            or not isinstance(body, dict) or set(body) != fields
            or body['observation_id'] != str(observation_id)
            or payload['review_digest'] != fingerprint(body)
            or row.pk != records._id('correction-review', company, fingerprint(body))
            or row.domain != 'accounting' or row.aggregate_root != str(provider.pk) or row.version != 1):
        raise AccountingError('Correction review identity or digest changed.')
    if (type(body['revision']) is not int or not 1 <= body['revision'] <= MAX_REVISIONS
            or not isinstance(body['previous_digest'], str) or not re.fullmatch('[0-9a-f]{64}',body['previous_digest'])
            or not isinstance(body['reason_code'], str) or body['reason_code'] not in REASONS
            or not isinstance(body['evidence_digest'], str) or not re.fullmatch('[0-9a-f]{64}',body['evidence_digest'])
            or not isinstance(body['reviewed_by'], str)):
        raise AccountingError('Correction metadata invalid.')
    _validate_assessment(company, original, body['assessment'])
    return row, body

def _factors(company, provider, assessment, *, persist=False):
    for factor in assessment['snapshot']['factors']:
        key = records._factor_key(factor)
        identifier = records._id('factor', company, key)
        payload = records._claim_payload(company, provider, 'factor', key, factor)
        if persist:
            records._write(identifier, records.FACTOR, provider, payload)
        row = OutboxEvent.objects.using('default').filter(pk=identifier, event_type=records.FACTOR).first()
        if row is None or row.payload != payload or row.domain != 'accounting' or row.aggregate_root != str(provider.pk) or row.version != 1:
            raise AccountingError('Immutable factor version evidence changed.')

def _chain(company, provider, observation_id):
    root, original = _root(company, provider, observation_id)
    rows = list(OutboxEvent.objects.using('default').filter(event_type=CORRECTED,
        payload__company_id=str(company.pk), payload__provider_id=str(provider.pk),
        payload__observation_id=str(root.pk)).order_by('payload__revision')[:MAX_REVISIONS+1])
    if len(rows) > MAX_REVISIONS:
        raise AccountingError('Correction history requires a reviewed extended migration.')
    digest = root.payload['record_digest']; assessment = original; history = []; revision = 0
    for row in rows:
        if not isinstance(row.payload, dict):raise AccountingError('Correction record malformed.')
        review, body = _review(company, provider, row.payload.get('review_id'), original, root.pk)
        revision += 1
        expected = {'company_id':str(company.pk), 'provider_id':str(provider.pk),
            'observation_id':str(root.pk), 'revision':revision, 'previous_digest':digest,
            'review_id':str(review.pk), 'review_digest':fingerprint(body), 'known_at':row.created_at.isoformat()}
        if (row.payload != {**expected, 'correction_digest':fingerprint(expected)}
                or body['revision'] != revision or body['previous_digest'] != digest
                or row.pk != records._id('correction-record', company, str(review.pk))
                or row.domain != 'accounting' or row.aggregate_root != str(provider.pk) or row.version != 1
                or row.created_at < review.created_at or review.created_at < root.created_at
                or body['assessment'] == assessment):
            raise AccountingError('Correction chain incomplete or altered.')
        _factors(company, provider, body['assessment'])
        digest = row.payload['correction_digest']; assessment = body['assessment']
        history.append({'correction_id':str(row.pk), 'review_id':str(review.pk),
            'revision':revision, 'previous_digest':body['previous_digest'], 'correction_digest':digest,
            'known_at':row.created_at.isoformat(), 'reason_code':body['reason_code']})
    return {'observation_id':str(root.pk), 'revision':revision, 'head_digest':digest,
            'original_assessment':original, 'effective_assessment':assessment, 'history':history}

@transaction.atomic
def correction_state(*, actor, provider_id, observation_id):
    _, provider, company = _context(actor, provider_id)
    return {**records._flags(company), **_chain(company, provider, observation_id),
            'read_only':True, 'confirmations_restored':False, 'original_preserved':True,
            'effective_total_replaces_original':True, 'esg_certified':False}

@transaction.atomic
def review_correction(*, actor, provider_id, observation_id, expected_revision,
                      activities, factors, evidence_digest, reason_code, confirmed):
    user, provider, company = _context(actor, provider_id)
    if (confirmed is not True or type(expected_revision) is not int or expected_revision < 0
            or not isinstance(reason_code, str) or reason_code not in REASONS
            or not isinstance(evidence_digest, str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest)):
        raise AccountingError('First correction review and explicit evidence required.')
    head = _chain(company, provider, observation_id)
    if expected_revision != head['revision'] or expected_revision >= MAX_REVISIONS:
        raise AccountingError('Correction revision changed or limit reached; reload history.')
    assessment = estimate(company_id=company.pk, activities=activities, factors=factors)
    _validate_assessment(company, head['original_assessment'], assessment)
    if assessment == head['effective_assessment']:
        raise AccountingError('No changed observation values; evidence alone is not a correction.')
    body = {'observation_id':head['observation_id'], 'revision':expected_revision+1,
        'previous_digest':head['head_digest'], 'assessment':assessment, 'reason_code':reason_code,
        'evidence_digest':evidence_digest, 'reviewed_by':str(user.pk)}
    identifier = records._id('correction-review', company, fingerprint(body))
    records._write(identifier, REVIEW, provider, {'company_id':str(company.pk),
        'provider_id':str(provider.pk), 'review':body, 'review_digest':fingerprint(body)})
    return {**records._flags(company), 'review_id':str(identifier), 'observation_id':head['observation_id'],
            'preview':body, 'confirmed':False, 'esg_certified':False}

@transaction.atomic
def record_correction(*, actor, provider_id, observation_id, review_id, confirmed):
    user, provider, company = _context(actor, provider_id)
    if confirmed is not True:
        raise AccountingError('Second explicit correction confirmation required.')
    head = _chain(company, provider, observation_id)
    review, body = _review(company, provider, review_id, head['original_assessment'], head['observation_id'])
    if body['reviewed_by'] != str(user.pk):
        raise AccountingError('Only the same requesting owner may confirm the correction.')
    identifier = records._id('correction-record', company, str(review.pk))
    existing = next((item for item in head['history'] if item['correction_id'] == str(identifier)), None)
    if existing:
        return {**records._flags(company), **existing, 'observation_id':head['observation_id'],
                'replayed':True, 'original_preserved':True, 'esg_certified':False}
    if body['revision'] != head['revision']+1 or body['previous_digest'] != head['head_digest']:
        raise AccountingError('Another correction advanced the observation; review again.')
    _factors(company, provider, body['assessment'], persist=True)
    row = records._write(identifier, CORRECTED, provider, {'company_id':str(company.pk),
        'provider_id':str(provider.pk), 'observation_id':head['observation_id'], 'revision':body['revision'],
        'previous_digest':head['head_digest'], 'review_id':str(review.pk), 'review_digest':fingerprint(body)})
    seal = {**row.payload, 'known_at':row.created_at.isoformat()}; seal['correction_digest'] = fingerprint(seal)
    OutboxEvent.objects.using('default').filter(pk=row.pk).update(payload=seal)
    updated = _chain(company, provider, observation_id)
    item = updated['history'][-1]
    return {**records._flags(company), **item, 'observation_id':head['observation_id'],
            'replayed':False, 'original_preserved':True, 'esg_certified':False}
