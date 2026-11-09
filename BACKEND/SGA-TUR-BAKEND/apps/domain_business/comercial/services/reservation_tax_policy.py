"""Recorded declared policy -> fiscal reservation review -> existing ledger flow.

No statutory determination, DIAN issuance, payment or withholding recognition.
The source, policy versions and exact quotes are rechecked on request/posting.
"""
import re
from uuid import UUID,uuid5
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.core_erp.accounting import tax_policies
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.outbox_models import OutboxEvent
from . import reservation_fiscal as fiscal

NS=UUID('b3d63be6-46ef-4582-bce6-65c72d905035')
EVENT='commercial.reservation.tax-policy-linked.v1'
PREFIX='SGATP/'
FIELDS={'item_id','net','tax_category','policy_code','policy_revision'}

def proof_id(review_id):return uuid5(NS,'policy-link:'+str(review_id))

def calculate(company,selection,economic_date):
    if not isinstance(selection,list) or not 1<=len(selection)<=5:
        raise ValidationError('Selecciona entre1 y5 componentes con política explícita.')
    seen=set();tax_codes=set();normalized=[];quotes=[];items=[]
    for row in selection:
        if not isinstance(row,dict) or set(row)!=FIELDS:
            raise ValidationError('Contrato de selección tributaria inválido.')
        if not isinstance(row['item_id'],str) or str(UUID(row['item_id']))!=row['item_id'] or row['item_id'] in seen:
            raise ValidationError('Identificador único de componente requerido.')
        seen.add(row['item_id'])
        quote=tax_policies.quote_policy(company.pk,code=row['policy_code'],revision=row['policy_revision'],
            economic_date=economic_date,net=row['net'],tax_category=row['tax_category'],direction='SALE')
        if quote['withholding']!='0.00':
            raise ValidationError('Las retenciones requieren un flujo contable completo; no se omiten silenciosamente.')
        tax_codes.update(c['code'] for c in quote['components'] if c['kind']=='OUTPUT_TAX' and c['amount']!='0.00')
        if len(tax_codes)>1:
            raise ValidationError('Varios impuestos requieren cuentas y posteo por componente; no se agrupan silenciosamente.')
        reference=PREFIX+row['policy_code']+'/'+str(row['policy_revision'])+'/'+quote['policy_digest']
        normalized.append(dict(row));quotes.append({'item_id':row['item_id'],'quote':quote})
        items.append({'item_id':row['item_id'],'net':row['net'],'tax':quote['output_tax'],
            'tax_category':row['tax_category'],'policy_reference':reference})
    return (sorted(normalized,key=lambda x:x['item_id']),sorted(quotes,key=lambda x:x['item_id']),sorted(items,key=lambda x:x['item_id']))

def validate_link(review,company,source,intent,source_fingerprint,recognition_date=None):
    """Called from the existing fiscal validator, including recognition posting.

    A reserved policy reference without its proof is never treated as manual.
    Ordinary historical manual reviews retain their existing behavior.
    """
    row=OutboxEvent.objects.filter(pk=proof_id(review.pk)).first()
    reserved=any(item['policy_reference'].startswith(PREFIX) for item in intent['payload']['items'])
    if row is None:
        if reserved:raise ValidationError('Falta la evidencia de política ligada a esta revisión.')
        return None
    payload=row.payload
    if (row.event_type!=EVENT or row.domain!='commercial' or row.aggregate_root!=str(source.pk) or row.version!=1
            or not isinstance(payload,dict) or set(payload)!={'schema','proof','proof_digest'}
            or payload['schema']!='sgacd-reservation-tax-policy-link-v1'):
        raise ValidationError('Identidad de evidencia tributaria incompatible.')
    body=payload['proof']
    fields={'company_id','reservation_id','fiscal_review_id','reviewed_by','economic_date',
            'selection','quotes','intent_digest','source_fingerprint','evidence_digest'}
    if (not isinstance(body,dict) or set(body)!=fields or payload['proof_digest']!=fingerprint(body)
            or body['company_id']!=str(company.pk) or body['reservation_id']!=str(source.pk)
            or body['fiscal_review_id']!=str(review.pk) or body['reviewed_by']!=review.payload['reviewed_by']
            or body['intent_digest']!=intent['payload_digest'] or body['source_fingerprint']!=source_fingerprint
            or body['evidence_digest']!=review.payload['evidence_digest']):
        raise ValidationError('La evidencia tributaria no corresponde a esta fuente y revisión.')
    if recognition_date is not None and recognition_date!=body['economic_date']:
        raise ValidationError('Este flujo exige fecha contable igual a la fecha tributaria revisada; diferencias requieren otro tratamiento explícito.')
    normalized,quotes,items=calculate(company,body['selection'],body['economic_date'])
    if normalized!=body['selection'] or quotes!=body['quotes'] or items!=intent['payload']['items']:
        raise ValidationError('La versión/política o el desglose revisado cambiaron.')
    return body

@transaction.atomic
def review_with_policy(*,actor,provider_id,reservation_id,selection,economic_date,evidence_digest,confirmed,expected_revision):
    user,company,source,source_fingerprint=fiscal.locked_source(actor,provider_id,reservation_id)
    if getattr(user,'is_agent',False):raise ValidationError('Se requiere un titular personal.')
    normalized,quotes,items=calculate(company,selection,economic_date)
    result=fiscal.review_reservation(actor=user,provider_id=provider_id,reservation_id=source.pk,
        items=items,evidence_digest=evidence_digest,confirmed=confirmed,expected_revision=expected_revision)
    review=OutboxEvent.objects.get(pk=result['review_id'])
    body={'company_id':str(company.pk),'reservation_id':str(source.pk),'fiscal_review_id':str(review.pk),
        'reviewed_by':str(user.pk),'economic_date':economic_date,'selection':normalized,'quotes':quotes,
        'intent_digest':review.payload['intent_digest'],'source_fingerprint':source_fingerprint,
        'evidence_digest':evidence_digest}
    proof=OutboxEvent.objects.create(id=proof_id(review.pk),event_type=EVENT,domain='commercial',
        aggregate_root=str(source.pk),payload={'schema':'sgacd-reservation-tax-policy-link-v1',
            'proof':body,'proof_digest':fingerprint(body)},version=1)
    fiscal.validated_review(review,company,source,source_fingerprint)
    return {**result,'company_id':str(company.pk),'reservation_id':str(source.pk),
        'policy_link_id':str(proof.pk),'policy_link_digest':proof.payload['proof_digest'],
        'preview':body,'stored_policy_link_verified':True,'regulatory_verified':False,
        'withholding_posted':False,'fiscal_document_created':False,'money_transferred':False}
