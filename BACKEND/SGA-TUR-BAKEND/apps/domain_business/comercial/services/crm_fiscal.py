"""Reviewed ownership of existing global CRM records; never a payment or invoice.

Binding is an internal independent-operator action. A company owner cannot claim
an arbitrary lead/opportunity by supplying its UUID. No legacy CRM row is moved.
"""
from datetime import datetime,timedelta
from uuid import UUID,uuid5
import re
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError,PermissionDenied
from apps.comercial.models import Opportunity
from apps.turismo.models import TourismProvider,VerifiedCompanyLink
from apps.turismo.services.company_identity import resolve_company
from apps.core_erp.accounting.validation import current_actor,lock_company,money
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_intent import prepare_invoice_intent
from apps.core_erp.accounting.invoice_queue import enqueue_invoice_intent,EVENT_TYPE
from apps.core_erp.outbox_models import OutboxEvent

BIND_EVENT='commercial.crm.company-bound.v1'
REVIEW_EVENT='commercial.crm.fiscal-review.v1'
BIND_NS=UUID('6e009444-fac5-482c-bbde-a73e6f005c31')
REVIEW_NS=UUID('e3ed582f-572f-4462-a5bb-254671115422')
FLAGS={'ledger_written':False,'fiscal_accepted':False,'money_transferred':False,'payment_verified':False,'published':False}

def evidence(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise ValidationError('Huella de soporte requerida.')

def envelope(row,event,schema,fields):
    if row is None or row.event_type!=event or row.domain!='commercial' or row.version!=1:raise ValidationError('Falta un registro comercial compatible.')
    p=row.payload
    if not isinstance(p,dict) or set(p)!={'schema','proof','proof_digest'} or p['schema']!=schema or not isinstance(p['proof'],dict) or set(p['proof'])!=fields or fingerprint(p['proof'])!=p['proof_digest']:raise ValidationError('El registro comercial cambió; requiere conciliación.')
    return p['proof']

BIND_FIELDS={'company_id','provider_id','source_id','lead_id','administrator_id','reviewer_id','evidence_digest','reviewed_at','valid_until'}

@transaction.atomic
def bind_crm_source(*,operator,provider_id,opportunity_id,evidence_digest,valid_until,apply=False):
    """Explicit independent ownership review, dry-run by default; no public route."""
    op=current_actor(operator)
    if not op.is_superuser:raise PermissionDenied('Se requiere revisión independiente autorizada.')
    if type(apply) is not bool:raise ValidationError('Aplicación explícita requerida.')
    evidence(evidence_digest);now=timezone.now()
    if not isinstance(valid_until,datetime) or not timezone.is_aware(valid_until) or not now<valid_until<=now+timedelta(days=30):raise ValidationError('Vigencia explícita máxima de treinta días.')
    provider=TourismProvider.objects.select_related('owner').get(pk=provider_id)
    initial=resolve_company(provider.owner,provider_id);lock_company(initial.tenant_id)
    VerifiedCompanyLink.objects.select_for_update().get(pk=initial.pk);provider=TourismProvider.objects.select_for_update(of=('self',)).select_related('owner').get(pk=provider_id)
    link=resolve_company(provider.owner,provider_id)
    if link.tenant_id!=initial.tenant_id or op.pk==provider.owner_id:raise PermissionDenied('Revisión independiente del titular requerida.')
    op=get_user_model().objects.select_for_update().filter(pk=op.pk,is_active=True,is_superuser=True).first()
    if op is None:raise PermissionDenied('El revisor dejó de estar autorizado.')
    source=Opportunity.objects.select_for_update().get(pk=UUID(str(opportunity_id)))
    identifier=uuid5(BIND_NS,str(source.pk))
    if OutboxEvent.objects.filter(pk=identifier).exists():raise ValidationError('Vínculo existente: no se reasigna ni renueva sin recuperación revisada.')
    body={'company_id':str(link.tenant_id),'provider_id':str(provider.pk),'source_id':str(source.pk),'lead_id':str(source.lead_id),'administrator_id':str(provider.owner_id),'reviewer_id':str(op.pk),'evidence_digest':evidence_digest,'reviewed_at':now.isoformat(),'valid_until':valid_until.isoformat()}
    if apply:OutboxEvent.objects.create(id=identifier,event_type=BIND_EVENT,domain='commercial',aggregate_root=str(source.pk),version=1,payload={'schema':'sgacd-crm-company-binding-v1','proof':body,'proof_digest':fingerprint(body)})
    return {'binding_id':str(identifier),'binding_recorded':apply,**FLAGS}


def locked_source(actor,provider_id,opportunity_id):
    user=current_actor(actor);initial=resolve_company(user,provider_id);company=lock_company(initial.tenant_id)
    VerifiedCompanyLink.objects.select_for_update().get(pk=initial.pk);TourismProvider.objects.select_for_update().get(pk=provider_id)
    link=resolve_company(user,provider_id)
    if link.tenant_id!=company.pk:raise PermissionDenied('La empresa cambió.')
    source_id=UUID(str(opportunity_id));row=OutboxEvent.objects.select_for_update().filter(pk=uuid5(BIND_NS,str(source_id)),payload__proof__company_id=str(company.pk)).first()
    body=envelope(row,BIND_EVENT,'sgacd-crm-company-binding-v1',BIND_FIELDS)
    if body['company_id']!=str(company.pk) or body['provider_id']!=str(provider_id) or body['source_id']!=str(source_id) or row.aggregate_root!=str(source_id) or body['administrator_id']!=str(user.pk) or body['reviewer_id']==str(user.pk):raise PermissionDenied('La oportunidad no pertenece al titular y empresa revisados.')
    for key in ('administrator_id','reviewer_id'):
        if not isinstance(body[key],str) or not re.fullmatch('[1-9][0-9]*',body[key]):raise ValidationError('Identidad de revisor CRM inválida.')
    reviewer=get_user_model().objects.filter(pk=body['reviewer_id'],is_active=True,is_superuser=True).first()
    try:reviewed=datetime.fromisoformat(body['reviewed_at']);until=datetime.fromisoformat(body['valid_until'])
    except (TypeError,ValueError):raise ValidationError('Vigencia CRM inválida.') from None
    if reviewer is None or reviewer.pk==user.pk or not timezone.is_aware(reviewed) or not timezone.is_aware(until) or not reviewed<=timezone.now()<until or until-reviewed>timedelta(days=30):raise PermissionDenied('El vínculo CRM no está vigente.')
    evidence(body['evidence_digest'])
    source=Opportunity.objects.select_for_update().filter(pk=source_id).first()
    if source is None or source.stage!=Opportunity.Stage.WON or str(source.lead_id)!=body['lead_id']:raise ValidationError('Se requiere oportunidad ganada y cliente revisado sin cambios.')
    gross=money(source.estimated_revenue)
    if gross<=0:raise ValidationError('Valor comercial positivo requerido.')
    digest=fingerprint({'company_id':str(company.pk),'opportunity_id':str(source.pk),'lead_id':str(source.lead_id),'stage':source.stage,'gross':format(gross,'.2f'),'currency':company.currency,'binding_digest':row.payload['proof_digest']})
    return user,company,source,digest

REVIEW_FIELDS={'company_id','source_id','review_revision','reviewed_by','source_fingerprint','snapshot','intent_digest','evidence_digest'}

def latest(company,source):
    return OutboxEvent.objects.filter(event_type=REVIEW_EVENT,domain='commercial',aggregate_root=str(source.pk),payload__proof__company_id=str(company.pk)).order_by('-payload__proof__review_revision').first()

def checked_review(row,company,source):
    p=envelope(row,REVIEW_EVENT,'sgacd-crm-fiscal-review-v1',REVIEW_FIELDS)
    revision=p['review_revision']
    if type(revision) is not int or not 1<=revision<=2147483647 or row.pk!=uuid5(REVIEW_NS,':'.join([str(company.pk),str(source.pk),str(revision)])) or row.aggregate_root!=str(source.pk) or p['company_id']!=str(company.pk) or p['source_id']!=str(source.pk):raise ValidationError('Identidad de revisión CRM incompatible.')
    evidence(p['evidence_digest']);intent=prepare_invoice_intent(p['snapshot'],str(company.pk))
    if intent['payload_digest']!=p['intent_digest'] or intent['payload']['source_type']!='crm_opportunity' or intent['payload']['source_id']!=str(source.pk) or intent['payload']['revision']!=revision:raise ValidationError('Contrato CRM incompatible.')
    return p,intent

@transaction.atomic
def review_crm_invoice(*,actor,provider_id,opportunity_id,items,evidence_digest,expected_revision,confirmed):
    if confirmed is not True or type(expected_revision) is not int or not 0<=expected_revision<2147483647:raise ValidationError('Revisión y confirmación explícitas requeridas.')
    evidence(evidence_digest);user,company,source,digest=locked_source(actor,provider_id,opportunity_id)
    if OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(source.pk),payload__company_id=str(company.pk)).exists():raise ValidationError('La solicitud existe; no se crea otra revisión para duplicarla.')
    prior=latest(company,source);previous=checked_review(prior,company,source)[0]['review_revision'] if prior else 0
    if previous!=expected_revision:raise ValidationError('Conflicto de revisión CRM; recarga.')
    revision=previous+1;snapshot={'schema':'sgacd-invoice-intent-v1','company_id':str(company.pk),'source_type':'crm_opportunity','source_id':str(source.pk),'revision':revision,'state':'WON','currency':company.currency,'items':items}
    intent=prepare_invoice_intent(snapshot,str(company.pk))
    if intent['payload']['totals']['gross']!=format(money(source.estimated_revenue),'.2f'):raise ValidationError('El desglose no coincide con el valor CRM.')
    body={'company_id':str(company.pk),'source_id':str(source.pk),'review_revision':revision,'reviewed_by':str(user.pk),'source_fingerprint':digest,'snapshot':snapshot,'intent_digest':intent['payload_digest'],'evidence_digest':evidence_digest}
    row=OutboxEvent.objects.create(id=uuid5(REVIEW_NS,':'.join([str(company.pk),str(source.pk),str(revision)])),event_type=REVIEW_EVENT,domain='commercial',aggregate_root=str(source.pk),version=1,payload={'schema':'sgacd-crm-fiscal-review-v1','proof':body,'proof_digest':fingerprint(body)})
    return {'schema':'sgacd-commercial-request-result-v1','company_id':str(company.pk),'source_id':str(source.pk),'source_type':'crm_opportunity','review_id':str(row.pk),'revision':revision,'request_created':False,'status':'REVIEWED',**FLAGS}

@transaction.atomic
def request_crm_invoice(*,actor,provider_id,opportunity_id,review_id,confirmed):
    if confirmed is not True:raise ValidationError('Segunda confirmación explícita requerida.')
    user,company,source,digest=locked_source(actor,provider_id,opportunity_id);row=latest(company,source)
    if row is None or str(row.pk)!=str(UUID(str(review_id))):raise ValidationError('Debe usarse la última revisión CRM.')
    p,intent=checked_review(row,company,source)
    if p['source_fingerprint']!=digest or p['reviewed_by']!=str(user.pk) or intent['payload']['totals']['gross']!=format(money(source.estimated_revenue),'.2f'):raise ValidationError('El origen o su titular cambió; requiere revisión.')
    result=enqueue_invoice_intent(p['snapshot'],company_id=company.pk,actor=user,source_review={'review_id':str(row.pk),'intent_digest':p['intent_digest'],'source_fingerprint':digest,'evidence_digest':p['evidence_digest']})
    return {**result,'schema':'sgacd-commercial-request-result-v1','company_id':str(company.pk),'source_id':str(source.pk),'source_type':'crm_opportunity','review_id':str(row.pk),'revision':p['review_revision'],'status':'REQUEST_ONLY','source_authority_verified':True,'legal_tax_policy_verified':False,**FLAGS}

@transaction.atomic
def reviewed_crm_ubl_source(*,actor,provider_id,opportunity_id,review_id):
    """Current reviewed CRM snapshot for local drafting; no fiscal artifact issued."""
    user,company,source,digest=locked_source(actor,provider_id,opportunity_id);row=latest(company,source)
    if row is None or str(row.pk)!=str(UUID(str(review_id))):raise ValidationError('Debe usarse la última revisión CRM.')
    p,intent=checked_review(row,company,source)
    if p['source_fingerprint']!=digest or p['reviewed_by']!=str(user.pk) or intent['payload']['totals']['gross']!=format(money(source.estimated_revenue),'.2f'):raise ValidationError('La fuente CRM cambió; requiere revisión.')
    return {'schema':'sgacd-reviewed-ubl-source-v1','company_id':str(company.pk),'review_id':str(row.pk),'source_fingerprint':digest,'intent_digest':intent['payload_digest'],'snapshot':intent['payload'],'read_only':True,'ledger_written':False,'fiscal_accepted':False,'legal_tax_policy_verified':False,'identity_independently_verified':False}
