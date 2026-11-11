"""Paged source/review/result contracts; never turns reference into certification."""
import hashlib,json
from decimal import Decimal
from datetime import date
from .reviewed_fx_contract import identifier,digest,amount

def fp(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def record(r):
    identifier(r['account_id']);digest(r['name_digest']);v=Decimal(r['initial_balance']);value=amount(format(abs(v),'.2f'))
    if not value or format(v,'.2f')!=r['initial_balance'] or r['type'] not in {'ASSET','LIABILITY','EQUITY'} or not isinstance(r['code'],str) or not r['code']:raise ValueError('Canonical preserved balance-sheet source required.')
    debit=(r['type']=='ASSET')==(v>0)
    if r['debit']!=format(value if debit else Decimal(0),'.2f') or r['credit']!=format(value if not debit else Decimal(0),'.2f'):raise ValueError('Source balance and proposed sides differ.')
def body(b,context):
    if b['company_id']!=context['tenant_id'] or b['reviewed_by']!=context['ledger_actor_id'] or b['mode']!='CHUNKED_SOURCE' or b['source_independently_verified'] is not False or type(b['revision']) is not int or b['revision']<1 or type(b['account_count']) is not int or not 2<=b['account_count']<=250 or type(b['chunk_count']) is not int or b['chunk_count']!=(b['account_count']+49)//50 or b['total_debit']!=b['total_credit'] or amount(b['total_debit'])<=0:raise ValueError('Opening manifest scope, count, verification or totals changed.')
    identifier(b['period_id']);digest(b['source_root_digest']);digest(b['evidence_digest'])
def validate(operation,data,payload,context):
    if data.get('company_id')!=context['tenant_id'] or any(data.get(k) is not False for k in ['money_transferred','source_independently_verified']) or data.get('source_fields_preserved') is not True:raise ValueError('Preserved opening scope/qualification changed.')
    if operation=='opening_chunks_sources':
        if data.get('schema')!='sgacd-opening-chunks-sources-v1' or data.get('read_only') is not True or data.get('ledger_written') is not False or data.get('confirmations_restored') is not False or not isinstance(data.get('rows'),list) or len(data['rows'])>50 or type(data.get('account_count')) is not int or not 0<=data['account_count']<=250 or type(data.get('can_review')) is not bool:raise ValueError('Bounded read-only source page required.')
        if date.fromisoformat(data['business_date']).isoformat()!=data['business_date']:raise ValueError('Canonical server business date required.')
        digest(data['source_root_digest']);ids=[]
        for r in data['rows']:
            record(r)
            if fp(r['name'])!=r['name_digest'] or type(r['active']) is not bool:raise ValueError('Displayed account name or active state changed.')
            ids.append(r['account_id'])
        if ids!=sorted(set(ids)) or payload.get('after_id') and any(i<=payload['after_id'] for i in ids):raise ValueError('Source page cursor/order changed.')
        if data['next_after'] is not None and (not ids or data['next_after']!=ids[-1]):raise ValueError('Unexpected source cursor.')
        return
    if operation=='opening_chunks_state':
        if data.get('schema')!='sgacd-opening-chunks-state-v1' or data.get('read_only') is not True or data.get('ledger_written') is not False or data.get('confirmations_restored') is not False or type(data.get('revision')) is not int:raise ValueError('Read-only current opening state required.')
        if data['preview'] is not None:
            body(data['preview'],context);identifier(data['review_id'])
            if data['revision']!=data['preview']['revision'] or type(data['source_current']) is not bool:raise ValueError('Recovered source revision changed.')
        elif data['revision']!=0 or data.get('applied') is not None:raise ValueError('Missing opening manifest.')
        if data.get('applied') is not None:
            validate('apply_opening_chunks',data['applied'],{'review_id':data['review_id']},context)
            if any(data['applied'][k]!=data['preview'][k] for k in ['account_count','chunk_count','source_root_digest','total_debit','total_credit']):raise ValueError('Applied opening differs from manifest.')
        return
    identifier(data['review_id'])
    if operation=='review_opening_chunks':
        if data.get('schema')!='sgacd-opening-chunks-review-v1' or data.get('ledger_written') is not False:raise ValueError('First opening confirmation cannot write ledger.')
        b=data['preview'];body(b,context)
        if b['entry_date']!=payload['entry_date'] or b['evidence_digest']!=payload['evidence_digest'] or b['source_root_digest']!=payload['source_root_digest'] or b['revision']!=payload['expected_revision']+1:raise ValueError('Requested opening manifest changed.')
    else:
        if data.get('schema')!='sgacd-opening-chunks-result-v1' or data['review_id']!=payload['review_id'] or data.get('ledger_written') is not True or type(data.get('reversed')) is not bool or type(data.get('replayed')) is not bool or not 2<=data['account_count']<=250 or data['total_debit']!=data['total_credit'] or amount(data['total_debit'])<=0:raise ValueError('Opening posting qualification changed.')
        identifier(data['journal_id']);digest(data['journal_hash']);digest(data['source_root_digest'])
