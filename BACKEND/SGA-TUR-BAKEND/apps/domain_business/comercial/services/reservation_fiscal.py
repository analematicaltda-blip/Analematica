"""Owner-reviewed reservation -> persisted fiscal review -> invoice request.
No legal tax determination, document emission, payment or external publication.
"""
import hashlib,json,re
from uuid import UUID,uuid5
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.core_erp.accounting.validation import current_actor,lock_company
from apps.core_erp.accounting.invoice_intent import prepare_invoice_intent
from apps.core_erp.accounting.invoice_queue import enqueue_invoice_intent,EVENT_TYPE
from apps.core_erp.outbox_models import OutboxEvent
from apps.turismo.models import TourismProvider,VerifiedCompanyLink
from apps.turismo.services.company_identity import resolve_company
from apps.domain_business.operativa.models import Reservation

REVIEW_EVENT='commercial.reservation.fiscal-review.v1'
NAMESPACE=UUID('f5f566fd-313d-4c45-a76c-58f8188b9d07')

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def locked_source(actor,provider_id,reservation_id,*,allowed_statuses=('CONFIRMED',)):
    reservation_id=UUID(str(reservation_id))
    user=current_actor(actor);initial=resolve_company(user,provider_id);company=lock_company(initial.tenant_id)
    VerifiedCompanyLink.objects.select_for_update().get(pk=initial.pk)
    TourismProvider.objects.select_for_update().get(pk=provider_id)
    link=resolve_company(user,provider_id)
    if link.tenant_id!=company.pk:raise ValidationError('La empresa cambió.')
    source=Reservation.plain_objects.select_for_update().filter(pk=reservation_id,tenant_id=company.pk).first()
    if source is None or source.status not in allowed_statuses:raise ValidationError('Se requiere reserva confirmada de esta empresa.')
    fingerprint={'company':str(company.pk),'reservation':str(source.pk),'customer':str(source.customer_id),
                 'content_type':source.content_type_id,'object':str(source.object_id),'start':source.start_date.isoformat(),
                 'end':source.end_date.isoformat(),'status':source.status,'gross':format(source.total_price,'.2f'),'currency':company.currency}
    return user,company,source,digest(fingerprint)

def latest_review(company,source):
    return OutboxEvent.objects.filter(event_type=REVIEW_EVENT,domain='commercial',aggregate_root=str(source.pk),
        payload__company_id=str(company.pk)).order_by('-payload__review_revision').first()

def validated_review(row,company,source,fingerprint,recognition_date=None):
    if row is None:raise ValidationError('Falta revisión fiscal persistida.')
    p=row.payload
    if not isinstance(p,dict) or p.get('source_fingerprint')!=fingerprint:raise ValidationError('La reserva cambió; requiere nueva revisión.')
    intent=prepare_invoice_intent(p.get('snapshot'),str(company.pk))
    snapshot=p['snapshot']
    if (snapshot['source_type']!='reservation' or snapshot['source_id']!=str(source.pk)
            or snapshot['state']!='CONFIRMED' or snapshot['currency']!=company.currency
            or intent['payload']['totals']['gross']!=format(source.total_price,'.2f')):
        raise ValidationError('El contrato no corresponde a esta reserva.')
    if intent['payload_digest']!=p.get('intent_digest') or row.version!=1 or p.get('review_revision')!=p['snapshot']['revision']:
        raise ValidationError('La revisión no coincide con su contrato.')
    if row.pk!=uuid5(NAMESPACE,':'.join([str(company.pk),str(source.pk),str(p['review_revision'])])):
        raise ValidationError('Identidad de revisión incompatible.')
    from .reservation_tax_policy import validate_link
    validate_link(row,company,source,intent,fingerprint,recognition_date=recognition_date)
    return p,intent

@transaction.atomic
def review_reservation(*,actor,provider_id,reservation_id,items,evidence_digest,confirmed,expected_revision):
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0:
        raise ValidationError('Se requiere confirmación y revisión esperada explícitas.')
    if not isinstance(evidence_digest,str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest):raise ValidationError('Huella de evidencia requerida.')
    user,company,source,fingerprint=locked_source(actor,provider_id,reservation_id)
    if OutboxEvent.objects.filter(event_type='accounting.reservation.recognized.v1',aggregate_root=str(source.pk),payload__company_id=str(company.pk)).exists():
        raise ValidationError('La reserva ya fue contabilizada; requiere ajuste explícito.')
    if OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(source.pk),payload__company_id=str(company.pk)).exists():
        raise ValidationError('La solicitud ya existe; los ajustes requieren otro flujo.')
    latest=latest_review(company,source);previous=latest.payload['review_revision'] if latest else 0
    if previous!=expected_revision:raise ValidationError('Conflicto de revisión; recarga antes de confirmar.')
    revision=previous+1
    snapshot={'schema':'sgacd-invoice-intent-v1','company_id':str(company.pk),'source_type':'reservation',
              'source_id':str(source.pk),'revision':revision,'state':source.status,'currency':company.currency,'items':items}
    intent=prepare_invoice_intent(snapshot,str(company.pk))
    if intent['payload']['totals']['gross']!=format(source.total_price,'.2f'):raise ValidationError('El desglose no coincide con el total de la reserva.')
    payload={'company_id':str(company.pk),'review_revision':revision,'reviewed_by':str(user.pk),
             'source_fingerprint':fingerprint,'snapshot':snapshot,'intent_digest':intent['payload_digest'],
             'evidence_digest':evidence_digest,'legal_tax_policy_verified':False}
    row=OutboxEvent.objects.create(id=uuid5(NAMESPACE,':'.join([str(company.pk),str(source.pk),str(revision)])),
        event_type=REVIEW_EVENT,domain='commercial',aggregate_root=str(source.pk),payload=payload,version=1)
    return {'review_id':str(row.pk),'revision':revision,'request_created':False,'fiscal_accepted':False,'ledger_written':False}

@transaction.atomic
def request_reservation_invoice(*,actor,provider_id,reservation_id,review_id,confirmed):
    if confirmed is not True:raise ValidationError('Se requiere una segunda confirmación explícita.')
    user,company,source,fingerprint=locked_source(actor,provider_id,reservation_id)
    row=latest_review(company,source)
    if row is None or str(row.pk)!=str(UUID(str(review_id))):raise ValidationError('Debe usarse la última revisión de esta reserva.')
    payload,intent=validated_review(row,company,source,fingerprint)
    if payload.get('reviewed_by')!=str(user.pk):raise ValidationError('La revisión pertenece a otro titular.')
    result=enqueue_invoice_intent(payload['snapshot'],company_id=company.pk,actor=user,source_review={
        'review_id':str(row.pk),'intent_digest':payload['intent_digest'],'source_fingerprint':fingerprint,
        'evidence_digest':payload['evidence_digest']})
    return {**result,'review_id':str(row.pk),'revision':payload['review_revision'],'source_authority_verified':True,
            'legal_tax_policy_verified':False}


def list_reservation_sources(*,actor,provider_id,after=None):
    from django.db.models import OuterRef,Subquery,Exists,CharField,Value,IntegerField
    from django.db.models.functions import Cast,Replace
    from django.db.models.fields.json import KeyTextTransform
    user=current_actor(actor);link=resolve_company(user,provider_id)
    reviews=OutboxEvent.objects.annotate(source_key=Replace('aggregate_root',Value('-'),Value(''))).filter(event_type=REVIEW_EVENT,domain='commercial',
        source_key=Replace(Cast(OuterRef('pk'),CharField()),Value('-'),Value('')),payload__company_id=str(link.tenant_id)).order_by('-payload__review_revision')
    requests=OutboxEvent.objects.annotate(source_key=Replace('aggregate_root',Value('-'),Value(''))).filter(event_type=EVENT_TYPE,source_key=Replace(Cast(OuterRef('pk'),CharField()),Value('-'),Value('')),payload__company_id=str(link.tenant_id))
    recognition_base=OutboxEvent.objects.annotate(source_key=Replace('aggregate_root',Value('-'),Value(''))).filter(
        source_key=Replace(Cast(OuterRef('pk'),CharField()),Value('-'),Value('')),payload__company_id=str(link.tenant_id))
    recognition_reviews=recognition_base.filter(event_type='accounting.reservation.recognition-reviewed.v1').order_by('-payload__revision')
    recognized=recognition_base.filter(event_type='accounting.reservation.recognized.v1').annotate(journal_ref=KeyTextTransform('journal_id','payload'))
    reversed_events=recognition_base.filter(event_type='accounting.reservation.reversed.v1')
    query=Reservation.plain_objects.filter(tenant_id=link.tenant_id,status='CONFIRMED')
    if after:query=query.filter(pk__gt=UUID(str(after)))
    rows=list(query.annotate(review_id=Subquery(reviews.values('pk')[:1]),
        review_revision=Cast(Subquery(reviews.values('payload__review_revision')[:1]),IntegerField()),request_created=Exists(requests),recognition_revision=Cast(Subquery(recognition_reviews.values('payload__revision')[:1]),IntegerField()),recognition_journal_id=Subquery(recognized.values('journal_ref')[:1]),recognition_reversed=Exists(reversed_events))
        .order_by('pk')[:21])
    return {'company_id':str(link.tenant_id),'currency':link.tenant.currency,'read_only':True,
        'sources':[{'reservation_id':str(row.pk),'gross':format(row.total_price,'.2f'),
            'start_date':row.start_date.isoformat(),'end_date':row.end_date.isoformat(),
            'review_id':str(row.review_id) if row.review_id else None,'revision':int(row.review_revision or 0),
            'request_created':row.request_created,'recognition_revision':int(row.recognition_revision or 0),'recognition_journal_id':row.recognition_journal_id,'recognition_reversed':row.recognition_reversed} for row in rows[:20]],
        'next_after':str(rows[19].pk) if len(rows)>20 else None}


@transaction.atomic
def reviewed_ubl_source(*,actor,provider_id,reservation_id,review_id):
    """Read a current owner-reviewed snapshot; never create a fiscal artifact."""
    user,company,source,fingerprint=locked_source(actor,provider_id,reservation_id)
    row=latest_review(company,source)
    if row is None or str(row.pk)!=str(UUID(str(review_id))):
        raise ValidationError('Debe usarse la última revisión de esta reserva.')
    payload,intent=validated_review(row,company,source,fingerprint)
    if payload.get('reviewed_by')!=str(user.pk):
        raise ValidationError('La revisión pertenece a otro titular.')
    return {'schema':'sgacd-reviewed-ubl-source-v1','company_id':str(company.pk),
        'review_id':str(row.pk),'source_fingerprint':fingerprint,
        'intent_digest':intent['payload_digest'],'snapshot':intent['payload'],
        'read_only':True,'ledger_written':False,'fiscal_accepted':False,
        'legal_tax_policy_verified':False,'identity_independently_verified':False}
