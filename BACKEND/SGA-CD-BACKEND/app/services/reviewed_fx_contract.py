"""Validate deterministic COP valuation returned by the authenticated ERP."""
from datetime import date,datetime
from decimal import Decimal,ROUND_HALF_UP,localcontext
import re
from uuid import UUID

def identifier(value):
    if not isinstance(value,str) or str(UUID(value))!=value:raise ValueError('Canonical FX identifier required.')
def digest(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise ValueError('FX digest required.')
def amount(value):
    if not isinstance(value,str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,15})\.[0-9]{2}',value):raise ValueError('Exact FX amount required.')
    return Decimal(value)
def source_shape(source,entry_id,actor):
    if not isinstance(source,dict) or set(source)!={'entry_id','date','period_id','description','reference','currency','base_currency','created_by','lines'} or source['entry_id']!=entry_id or source['currency'] not in ('USD','EUR') or source['base_currency']!='COP' or str(source['created_by'])!=actor:raise ValueError('Invalid scoped FX source.')
    identifier(entry_id);identifier(source['period_id'])
    if date.fromisoformat(source['date']).isoformat()!=source['date']:raise ValueError('Canonical FX date required.')
    lines=source['lines'];seen=set();debit=credit=Decimal('0')
    if not isinstance(lines,list) or not 2<=len(lines)<=100:raise ValueError('Bounded source lines required.')
    for line in lines:
        if not isinstance(line,dict) or set(line)!={'line_id','account_id','debit','credit','currency','description'} or line['currency']!=source['currency']:raise ValueError('Invalid source line.')
        identifier(line['line_id']);identifier(line['account_id']);left=amount(line['debit']);right=amount(line['credit'])
        if line['line_id'] in seen or (left>0)==(right>0):raise ValueError('Duplicate or unbalanced source line.')
        seen.add(line['line_id']);debit+=left;credit+=right
    if debit!=credit:raise ValueError('Source debit/credit differ.')

def preview(body,company_id,entry_id):
    if not isinstance(body,dict) or set(body)!={'company_id','reviewed_by','revision','source','quote','valuation','independently_verified'} or body['company_id']!=company_id or body['independently_verified'] is not False or type(body['revision']) is not int or body['revision']<1:raise ValueError('Invalid FX review.')
    source=body['source'];terms=body['quote'];valuation=body['valuation']
    source_shape(source,entry_id,body['reviewed_by'])
    if not isinstance(source,dict) or set(source)!={'entry_id','date','period_id','description','reference','currency','base_currency','created_by','lines'} or source['entry_id']!=entry_id or source['currency'] not in ('USD','EUR') or source['base_currency']!='COP' or str(source['created_by'])!=body['reviewed_by']:raise ValueError('Foreign FX source.')
    identifier(source['entry_id']);identifier(source['period_id']);day=date.fromisoformat(source['date'])
    if not isinstance(terms,dict) or set(terms)!={'base_currency','target_currency','rate','source_reference','source_version','observed_at','valid_from','valid_until','evidence_digest'} or terms['base_currency']!=source['currency'] or terms['target_currency']!='COP' or not isinstance(terms['rate'],str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,8})\.[0-9]{6}',terms['rate']) or Decimal(terms['rate'])<=0:raise ValueError('Invalid FX quote.')
    digest(terms['evidence_digest']);start=date.fromisoformat(terms['valid_from']);end=date.fromisoformat(terms['valid_until'])
    if not start<=day<=end or (end-start).days>366 or datetime.fromisoformat(terms['observed_at']).tzinfo is None:raise ValueError('Invalid FX validity.')
    for key in ('source_reference','source_version'):
        if not isinstance(terms[key],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}',terms[key]):raise ValueError('Bounded provenance required.')
    lines=source['lines'];seen=set();computed=[];debit=credit=Decimal('0');left_total=right_total=Decimal('0')
    if not isinstance(lines,list) or not 2<=len(lines)<=100:raise ValueError('Bounded FX lines required.')
    with localcontext() as context:
        context.prec=38
        for line in lines:
            if not isinstance(line,dict) or set(line)!={'line_id','account_id','debit','credit','currency','description'} or line['currency']!=source['currency']:raise ValueError('Invalid FX line.')
            identifier(line['line_id']);identifier(line['account_id'])
            if line['line_id'] in seen:raise ValueError('Duplicate FX line.')
            seen.add(line['line_id']);left=amount(line['debit']);right=amount(line['credit'])
            if (left>0)==(right>0):raise ValueError('Exactly one FX side required.')
            val=((left or right)*Decimal(terms['rate'])).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
            if val<=0 or val>Decimal('9999999999999999.99'):raise ValueError('FX amount out of range.')
            left_total+=left;right_total+=right;debit+=val if left else 0;credit+=val if right else 0
            computed.append({**line,'transaction_amount':format(left or right,'.2f'),'base_amount':format(val,'.2f')})
    if left_total!=right_total or debit!=credit or valuation!={'lines':computed,'total_debit_cop':format(debit,'.2f'),'total_credit_cop':format(credit,'.2f'),'rounding':'PER_LINE_HALF_UP'}:raise ValueError('FX valuation does not conserve amounts.')
    return body

def posted(data,company_id,entry_id):
    fields={'schema','company_id','entry_id','journal_id','review_id','journal_hash','currency','base_currency','exchange_rate','source_reference','source_version','total_debit_cop','total_credit_cop','original_reversed','replayed','ledger_written','money_transferred','rate_independently_verified','fiscal_accepted'}
    if not isinstance(data,dict) or set(data)!=fields or data['schema']!='sgacd-reviewed-fx-result-v1' or data['company_id']!=company_id or data['entry_id']!=entry_id or data['journal_id']!=entry_id or data['currency'] not in ('USD','EUR') or data['base_currency']!='COP' or data['ledger_written'] is not True or type(data['replayed']) is not bool or type(data['original_reversed']) is not bool or any(data[k] is not False for k in ('money_transferred','rate_independently_verified','fiscal_accepted')):raise ValueError('Invalid FX posting result.')
    identifier(entry_id);identifier(data['review_id']);digest(data['journal_hash'])
    for key in ('source_reference','source_version'):
        if not isinstance(data[key],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}',data[key]):raise ValueError('Invalid FX result provenance.')
    if not isinstance(data['exchange_rate'],str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,8})\.[0-9]{6}',data['exchange_rate']) or Decimal(data['exchange_rate'])<=0 or amount(data['total_debit_cop'])<=0 or data['total_debit_cop']!=data['total_credit_cop']:raise ValueError('Invalid FX result totals/rate.')

def validate(operation,data,payload,context):
    company_id=context['tenant_id']
    if operation=='foreign_journal_sources':
        if not isinstance(data,dict) or set(data)!={'company_id','sources','next_after','read_only','ledger_written','money_transferred','rate_independently_verified'} or data['company_id']!=company_id or data['read_only'] is not True or any(data[k] is not False for k in ('ledger_written','money_transferred','rate_independently_verified')) or not isinstance(data['sources'],list) or len(data['sources'])>20:raise ValueError('Invalid FX catalog.')
        seen=[]
        for source in data['sources']:
            if not isinstance(source,dict) or set(source)!={'entry_id','date','currency','description','review_pending'} or source['currency'] not in ('USD','EUR') or type(source['review_pending']) is not bool or not isinstance(source['description'],str):raise ValueError('Invalid FX catalog source.')
            identifier(source['entry_id']);date.fromisoformat(source['date']);seen.append(source['entry_id'])
        if seen!=sorted(set(seen)) or payload['after_id'] is not None and any(k<=payload['after_id'] for k in seen):raise ValueError('Invalid FX cursor order.')
        if data['next_after'] is not None and (len(seen)!=20 or data['next_after']!=seen[-1]):raise ValueError('Invalid FX next cursor.')
        return
    entry_id=payload['entry_id'];identifier(entry_id)
    if data.get('company_id')!=company_id or data.get('money_transferred') is not False or data.get('rate_independently_verified') is not False:raise ValueError('Foreign or overstated FX result.')
    if operation=='post_foreign_journal':
        posted(data,company_id,entry_id)
        if data['review_id']!=payload['review_id']:raise ValueError('Different FX review.')
    elif operation=='review_foreign_journal':
        if set(data)!={'company_id','review_id','preview','ledger_written','money_transferred','rate_independently_verified'} or data['ledger_written'] is not False:raise ValueError('Invalid FX review result.')
        identifier(data['review_id']);body=preview(data['preview'],company_id,entry_id)
        if body['quote']!=payload['terms'] or body['revision']!=payload['expected_revision']+1 or body['reviewed_by']!=context['ledger_actor_id']:raise ValueError('FX review differs from request.')
    else:
        if set(data)!={'company_id','entry_id','source','revision','review_id','preview','source_matches_review','applied','read_only','confirmations_restored','ledger_written','money_transferred','rate_independently_verified'} or data['entry_id']!=entry_id or data['read_only'] is not True or data['confirmations_restored'] is not False or data['ledger_written'] is not False:raise ValueError('Invalid FX state.')
        source_shape(data['source'],entry_id,context['ledger_actor_id'])
        if type(data['revision']) is not int or type(data['source_matches_review']) is not bool:raise ValueError('Invalid FX state revision.')
        if data['preview'] is None and (data['revision']!=0 or data['review_id'] is not None or data['applied'] is not None or data['source_matches_review']):raise ValueError('FX state claims missing review.')
        if data['preview'] is not None:
            body=preview(data['preview'],company_id,entry_id)
            if body['reviewed_by']!=context['ledger_actor_id'] or data['source_matches_review']!=(data['source']==body['source']) or data['revision']!=body['revision']:raise ValueError('FX source status differs.')
        if data['applied'] is not None:
            applied=data['applied'];posted(applied,company_id,entry_id)
            if applied['review_id']!=data['review_id'] or applied['exchange_rate']!=body['quote']['rate'] or applied['total_debit_cop']!=body['valuation']['total_debit_cop'] or applied['total_credit_cop']!=body['valuation']['total_credit_cop']:raise ValueError('Posted FX state differs from review.')
