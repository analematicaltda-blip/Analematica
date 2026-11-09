"""Owner-reviewed environmental observations. No liability, offset or payment.

Company locks serialize service writers. Outbox hashes detect inconsistency, not
privileged database rewriting; source digests are declarations, not certificates.
"""
import re
from uuid import UUID,uuid5
from django.db import transaction
from django.utils import timezone
from apps.core_erp.accounting.environmental import estimate
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from .tourism_metrics import _context

NS=UUID('2a381bf7-a5d8-4dd5-9fd9-d96614cba8ad')
REVIEW='accounting.environmental.reviewed.v1'
RECORDED='accounting.environmental.recorded.v1'
ACTIVITY='accounting.environmental.activity-claimed.v1'
FACTOR='accounting.environmental.factor-version.v1'


def _id(kind,company,key):return uuid5(NS,kind+':'+str(company.pk)+':'+key)
def _write(identifier,kind,provider,payload):
    row=OutboxEvent.objects.using('default').filter(pk=identifier).first()
    if row:
        if row.event_type!=kind or row.payload!=payload:raise AccountingError('Environmental identity already used by different evidence.')
    else:row=OutboxEvent.objects.using('default').create(id=identifier,event_type=kind,domain='accounting',aggregate_root=str(provider.pk),payload=payload,version=1)
    return row

def _flags(company):return {'company_id':str(company.pk),'ledger_written':False,'money_transferred':False,'liability_recognized':False,'carbon_credit_issued':False,'independently_verified':False}

def _review(company,provider,review_id):
    row=OutboxEvent.objects.using('default').filter(pk=UUID(str(review_id)),event_type=REVIEW,payload__company_id=str(company.pk),payload__provider_id=str(provider.pk)).first()
    body=row.payload.get('review') if row and isinstance(row.payload,dict) else None
    if not isinstance(body,dict) or set(body)!={'assessment','reviewed_by','evidence_digest'} or row.payload.get('review_digest')!=fingerprint(body) or row.pk!=_id('review',company,fingerprint(body)):raise AccountingError('Environmental review missing or inconsistent.')
    assessment=body['assessment']
    if not isinstance(assessment,dict) or not isinstance(assessment.get('snapshot'),dict):raise AccountingError('Environmental assessment malformed.')
    snapshot=assessment['snapshot']
    if snapshot.get('company_id')!=str(company.pk) or estimate(company_id=company.pk,activities=snapshot.get('activities'),factors=snapshot.get('factors'))!=assessment:raise AccountingError('Environmental sources no longer match review evidence.')
    if not isinstance(body['evidence_digest'],str) or not re.fullmatch('[0-9a-f]{64}',body['evidence_digest']):raise AccountingError('Missing activity support digest.')
    return row,body

def _claim_payload(company,provider,kind,key,content):
    return {'company_id':str(company.pk),'provider_id':str(provider.pk),'kind':kind,'key':key,'content':content,'content_digest':fingerprint(content)}

def _factor_key(factor):return factor['id']+':'+factor['version']

def _verify_record(company,provider,record,review,body):
    payload=record.payload
    expected={'company_id':str(company.pk),'provider_id':str(provider.pk),'review_id':str(review.pk),'review_digest':fingerprint(body),'known_at':record.created_at.isoformat()}
    if record.event_type!=RECORDED or record.pk!=_id('record',company,str(review.pk)) or payload!={**expected,'record_digest':fingerprint(expected)} or record.created_at<review.created_at:raise AccountingError('Environmental record evidence changed.')
    assessment=body['assessment']
    for factor in assessment['snapshot']['factors']:
        key=_factor_key(factor);row=OutboxEvent.objects.using('default').filter(pk=_id('factor',company,key),event_type=FACTOR).first()
        if row is None or row.payload!=_claim_payload(company,provider,'factor',key,factor):raise AccountingError('Environmental factor origin changed.')
    for activity in assessment['snapshot']['activities']:
        key=activity['id'];content={'activity':activity,'observation_id':str(record.pk)};row=OutboxEvent.objects.using('default').filter(pk=_id('activity',company,key),event_type=ACTIVITY).first()
        if row is None or row.payload!=_claim_payload(company,provider,'activity',key,content):raise AccountingError('Environmental activity claim changed.')
    return {'observation_id':str(record.pk),'known_at':record.created_at.isoformat(),'record_digest':payload['record_digest']}

@transaction.atomic
def review_measurement(*,actor,provider_id,activities,factors,evidence_digest,confirmed):
    user,provider,company=_context(actor,provider_id)
    if confirmed is not True or not isinstance(evidence_digest,str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest):raise AccountingError('First review and activity support digest required.')
    assessment=estimate(company_id=company.pk,activities=activities,factors=factors)
    if any(a['date']>timezone.localdate().isoformat() for a in assessment['snapshot']['activities']):raise AccountingError('Future activities may be estimated, not recorded as observed.')
    body={'assessment':assessment,'reviewed_by':str(user.pk),'evidence_digest':evidence_digest};identifier=_id('review',company,fingerprint(body))
    payload={'company_id':str(company.pk),'provider_id':str(provider.pk),'review':body,'review_digest':fingerprint(body)}
    _write(identifier,REVIEW,provider,payload)
    return {**_flags(company),'review_id':str(identifier),'preview':body,'confirmed':False}

@transaction.atomic
def record_measurement(*,actor,provider_id,review_id,confirmed):
    user,provider,company=_context(actor,provider_id)
    if confirmed is not True:raise AccountingError('Second explicit observation confirmation required.')
    review,body=_review(company,provider,review_id)
    if body['reviewed_by']!=str(user.pk):raise AccountingError('The requesting owner must confirm their own review.')
    identifier=_id('record',company,str(review.pk));existing=OutboxEvent.objects.using('default').filter(pk=identifier).first()
    if existing:
        result=_verify_record(company,provider,existing,review,body)
        return {**_flags(company),**result,'review_id':str(review.pk),'replayed':True}
    assessment=body['assessment']
    for factor in assessment['snapshot']['factors']:
        key=_factor_key(factor);_write(_id('factor',company,key),FACTOR,provider,_claim_payload(company,provider,'factor',key,factor))
    for activity in assessment['snapshot']['activities']:
        key=activity['id'];content={'activity':activity,'observation_id':str(identifier)}
        _write(_id('activity',company,key),ACTIVITY,provider,_claim_payload(company,provider,'activity',key,content))
    record=_write(identifier,RECORDED,provider,{'company_id':str(company.pk),'provider_id':str(provider.pk),'review_id':str(review.pk),'review_digest':fingerprint(body)})
    seal={**record.payload,'known_at':record.created_at.isoformat()};seal['record_digest']=fingerprint(seal)
    OutboxEvent.objects.using('default').filter(pk=record.pk).update(payload=seal);record.payload=seal
    result=_verify_record(company,provider,record,review,body)
    return {**_flags(company),**result,'review_id':str(review.pk),'replayed':False}

@transaction.atomic
def measurement_state(*,actor,provider_id,review_id):
    user,provider,company=_context(actor,provider_id);review,body=_review(company,provider,review_id)
    record=OutboxEvent.objects.using('default').filter(pk=_id('record',company,str(review.pk))).first()
    applied=_verify_record(company,provider,record,review,body) if record else None
    from .environmental_corrections import _chain
    corrections=_chain(company,provider,record.pk) if record else None
    return {**_flags(company),'corrections':corrections,'read_only':True,'review_id':str(review.pk),'preview':body,'reviewed_by_current_owner':body['reviewed_by']==str(user.pk),'applied':applied,'confirmations_restored':False}
