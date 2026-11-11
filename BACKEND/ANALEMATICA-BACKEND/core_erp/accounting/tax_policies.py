"""Versioned owner-declared tax rules, exact previews, no fiscal certification.
No statutory rates are inferred. Recording requires two separate confirmations.
"""
from datetime import date
import re
from uuid import UUID,uuid5
from django.db import transaction
from .validation import lock_company,current_actor
from .integrity import fingerprint
from .invoice_intent import _money,_format_money
from .exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent

NS=UUID('b5708b10-133c-4ea3-a706-0465ca381333')
REVIEW='accounting.tax-policy.reviewed.v1'
RECORDED='accounting.tax-policy.recorded.v1'
CATEGORIES={'TAXABLE','EXEMPT','EXCLUDED'}

def normalize(policy):
    if not isinstance(policy,dict) or set(policy)!={'code','jurisdiction','currency','valid_from','valid_until','rounding','components'}:raise AccountingError('Explicit supported tax policy required.')
    if not isinstance(policy['code'],str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,39}',policy['code']) or policy['jurisdiction']!='CO' or policy['currency']!='COP' or policy['rounding']!='PER_COMPONENT_HALF_UP':raise AccountingError('Unsupported policy identity, currency or rounding.')
    start=date.fromisoformat(policy['valid_from']);end=date.fromisoformat(policy['valid_until'])
    if start.isoformat()!=policy['valid_from'] or end.isoformat()!=policy['valid_until'] or start>end or (end-start).days>3660:raise AccountingError('Explicit bounded canonical policy validity required.')
    if not isinstance(policy['components'],list) or not 1<=len(policy['components'])<=20:raise AccountingError('One to20 explicit tax/withholding components required.')
    seen=set();components=[]
    for row in policy['components']:
        if not isinstance(row,dict) or set(row)!={'code','kind','rate_bps','applies_to'}:raise AccountingError('Invalid component contract.')
        if not isinstance(row['code'],str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,29}',row['code']) or row['code'] in seen or not isinstance(row['kind'],str) or row['kind'] not in {'OUTPUT_TAX','INPUT_TAX','WITHHOLDING'} or type(row['rate_bps']) is not int or not 0<=row['rate_bps']<=10000:raise AccountingError('Unique component and integer rate from0 to10000 basis points required.')
        categories=row['applies_to']
        if not isinstance(categories,list) or not categories or any(not isinstance(c,str) for c in categories) or len(categories)!=len(set(categories)) or not all(c in CATEGORIES for c in categories):raise AccountingError('Explicit nonduplicated tax categories required.')
        if row['kind'] in {'OUTPUT_TAX','INPUT_TAX'} and row['rate_bps']>0 and any(c in {'EXEMPT','EXCLUDED'} for c in categories):raise AccountingError('Do not charge output tax to exempt/excluded components.')
        seen.add(row['code']);components.append({**row,'applies_to':sorted(categories)})
    return {**policy,'components':sorted(components,key=lambda r:r['code'])}

def versions(company,code):
    return OutboxEvent.objects.filter(event_type=RECORDED,aggregate_root=str(company),payload__company_id=str(company),payload__code=code).order_by('-payload__revision')

def verified(row,company):
    body=row.payload.get('policy')
    if not isinstance(body,dict) or body.get('company_id')!=str(company) or fingerprint(body)!=row.payload.get('policy_digest') or row.payload.get('revision')!=body.get('revision') or row.payload.get('code')!=body.get('terms',{}).get('code'):raise AccountingError('Tax policy evidence changed.')
    if row.pk!=uuid5(NS,'recorded:'+str(company)+':'+body['terms']['code']+':'+str(body['revision'])):raise AccountingError('Tax policy identity mismatch.')
    normalize(body['terms'])
    return body

@transaction.atomic
def review_policy(company_id,*,actor,policy,evidence_digest,expected_revision,confirmed):
    company=lock_company(company_id);user=current_actor(actor);terms=normalize(policy)
    if company.currency!='COP' or confirmed is not True or type(expected_revision) is not int or expected_revision<0 or not isinstance(evidence_digest,str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest):raise AccountingError('COP scope, explicit review/revision and evidence required.')
    latest=versions(company.pk,terms['code']).first();previous=latest.payload['revision'] if latest else 0
    if previous!=expected_revision:raise AccountingError('Tax policy revision changed.')
    body={'company_id':str(company.pk),'reviewed_by':str(user.pk),'terms':terms,'evidence_digest':evidence_digest,'expected_revision':previous,'revision':previous+1,'regulatory_verified':False}
    identifier=uuid5(NS,'review:'+fingerprint(body));existing=OutboxEvent.objects.filter(pk=identifier).first();payload={'company_id':str(company.pk),'review':body,'review_digest':fingerprint(body)}
    if existing and (existing.event_type!=REVIEW or existing.payload!=payload):raise AccountingError('Tax review identity conflict.')
    if not existing:OutboxEvent.objects.create(id=identifier,event_type=REVIEW,domain='accounting',aggregate_root=str(company.pk),payload=payload,version=1)
    return {'company_id':str(company.pk),'review_id':str(identifier),'preview':body,'ledger_written':False,'regulatory_verified':False}

@transaction.atomic
def record_policy(company_id,*,actor,review_id,confirmed):
    company=lock_company(company_id);user=current_actor(actor)
    if confirmed is not True or company.currency!='COP':raise AccountingError('Second policy confirmation and COP company required.')
    row=OutboxEvent.objects.filter(pk=UUID(str(review_id)),event_type=REVIEW,payload__company_id=str(company.pk)).first()
    if row is None:raise AccountingError('Reviewed company tax policy required.')
    body=row.payload['review']
    if fingerprint(body)!=row.payload['review_digest'] or body['reviewed_by']!=str(user.pk):raise AccountingError('Review or reviewer changed.')
    terms=normalize(body['terms']);identifier=uuid5(NS,'recorded:'+str(company.pk)+':'+terms['code']+':'+str(body['revision']))
    payload={'company_id':str(company.pk),'code':terms['code'],'revision':body['revision'],'policy':body,'policy_digest':fingerprint(body),'review_id':str(row.pk)}
    existing=OutboxEvent.objects.filter(pk=identifier).first()
    if existing:
        if existing.event_type!=RECORDED or existing.payload!=payload:raise AccountingError('Conflicting policy version; no overwrite.')
        return {'company_id':str(company.pk),'policy_id':str(identifier),'revision':body['revision'],'replayed':True,'ledger_written':False,'regulatory_verified':False}
    records=list(versions(company.pk,terms['code'])[:201])
    if len(records)>200:raise AccountingError('Policy history requires separate review.')
    previous=records[0].payload['revision'] if records else 0
    if previous!=body['expected_revision']:raise AccountingError('Policy revision changed before confirmation.')
    for prior in records:
        old=verified(prior,company.pk)['terms']
        if terms['valid_from']<=old['valid_until'] and terms['valid_until']>=old['valid_from']:raise AccountingError('Policy validity overlaps an existing immutable version.')
    OutboxEvent.objects.create(id=identifier,event_type=RECORDED,domain='accounting',aggregate_root=str(company.pk),payload=payload,version=1)
    return {'company_id':str(company.pk),'policy_id':str(identifier),'revision':body['revision'],'replayed':False,'ledger_written':False,'regulatory_verified':False}

@transaction.atomic
def quote_policy(company_id,*,code,revision,economic_date,net,tax_category,direction):
    company=lock_company(company_id)
    if company.currency!='COP' or type(revision) is not int or revision<1 or not isinstance(code,str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,39}',code):raise AccountingError('Explicit COP company policy version required.')
    row=versions(company.pk,code).filter(payload__revision=revision).first()
    if row is None:raise AccountingError('No such recorded company policy.')
    body=verified(row,company.pk);terms=body['terms'];day=date.fromisoformat(economic_date)
    if any(r['kind']=='INPUT_TAX' for r in terms['components']):raise AccountingError('Input-tax policy requires the explicit reviewed purchase flow, never a sale quote.')
    if day.isoformat()!=economic_date or not terms['valid_from']<=economic_date<=terms['valid_until'] or tax_category not in CATEGORIES or direction not in {'SALE','CREDIT_NOTE'}:raise AccountingError('Date/category/direction incompatible with selected policy.')
    cents=_money(net)
    if cents<=0:raise AccountingError('Positive exact net amount required; use explicit credit-note direction.')
    taxes=withholdings=0;components=[]
    sign=1 if direction=='SALE' else -1
    def amount(value):return ('-' if sign<0 and value else '')+_format_money(value)
    for rule in terms['components']:
        applies=tax_category in rule['applies_to'];value=(cents*rule['rate_bps']+5000)//10000 if applies else 0
        if rule['kind']=='OUTPUT_TAX':taxes+=value
        else:withholdings+=value
        components.append({**rule,'basis':net,'applied':applies,'amount':amount(value),'rounding':terms['rounding']})
    payable=cents+taxes-withholdings
    if payable<0:raise AccountingError('Withholding exceeds the gross amount.')
    return {'schema':'sgacd-tax-quote-v1','company_id':str(company.pk),'policy_id':str(row.pk),'policy_revision':revision,'policy_digest':row.payload['policy_digest'],'economic_date':economic_date,'direction':direction,'tax_category':tax_category,'currency':'COP','net':amount(cents),'output_tax':amount(taxes),'withholding':amount(withholdings),'gross':amount(cents+taxes),'payable':amount(payable),'components':components,'read_only':True,'ledger_written':False,'regulatory_verified':False,'fiscal_document_created':False}

@transaction.atomic
def policy_history(company_id,*,code,before_revision=None):
    company=lock_company(company_id)
    if not isinstance(code,str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,39}',code):raise AccountingError('Policy code required.')
    query=versions(company.pk,code)
    if before_revision is not None:
        if not isinstance(before_revision,str) or not re.fullmatch('[1-9][0-9]{0,9}',before_revision):raise AccountingError('Invalid policy history cursor.')
        query=query.filter(payload__revision__lt=int(before_revision))
    found=list(query[:21]);items=[]
    for row in found[:20]:
        body=verified(row,company.pk);items.append({'policy_id':str(row.pk),'revision':body['revision'],'terms':body['terms'],'policy_digest':row.payload['policy_digest'],'regulatory_verified':False})
    return {'company_id':str(company.pk),'code':code,'read_only':True,'items':items,'next_before_revision':str(found[19].payload['revision']) if len(found)>20 else None}
