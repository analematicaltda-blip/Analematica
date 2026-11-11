"""Independent conservation and cumulative original-cent allocation checks."""
import re
from .native_purchase_contract import uuid,positive
from .purchase_concepts_contract import cents,fmt
FIELDS={'net','tax','withholding','gross','settlement'}
def money_totals(v):
    if not isinstance(v,dict) or set(v)!=FIELDS:raise ValueError('Exact return totals required.')
    n={k:cents(v[k]) for k in FIELDS}
    if n['net']+n['tax']!=n['gross'] or n['gross']-n['withholding']!=n['settlement']:raise ValueError('Return totals do not conserve value.')
    return n

def allocations(p,selection):
    if p['selection']!=sorted(selection,key=lambda a:a['item_id']) or not isinstance(p['allocations'],list) or len(p['allocations'])!=len(selection) or not 1<=len(selection)<=20:raise ValueError('Different return concepts.')
    seen=set();total={k:0 for k in FIELDS};expected=[]
    def line(account,n,debit,kind):
        if n:expected.append({'account_id':account,'debit':fmt(n if debit else 0),'credit':fmt(0 if debit else n),'kind':kind})
    for a,s in zip(p['allocations'],p['selection']):
        if set(s)!={'item_id','net'} or set(a)!={'item_id','basis_account_id','original_net','previous_net','net','new_net','components','totals'} or a['item_id']!=s['item_id'] or a['net']!=s['net']:raise ValueError('Allocation identity differs.')
        uuid(a['item_id']);uuid(a['basis_account_id']);original=cents(a['original_net']);before=cents(a['previous_net']);net=cents(a['net']);after=cents(a['new_net'])
        if a['item_id'] in seen or original<=0 or net<=0 or before+net!=after or after>original:raise ValueError('Concept capacity exceeded.')
        seen.add(a['item_id']);tax=ret=orig_tax=orig_ret=new_tax=new_ret=0;codes=set();line(a['basis_account_id'],net,False,'BASIS')
        if not isinstance(a['components'],list) or len(a['components'])>20:raise ValueError('Bounded original tax components required.')
        for c in a['components']:
            if set(c)!={'code','kind','account_id','original_amount','previous_amount','new_amount','delta_amount'} or c['kind'] not in {'INPUT_TAX','WITHHOLDING','OUTPUT_TAX'} or not isinstance(c['code'],str) or c['code'] in codes:raise ValueError('Invalid original return component.')
            codes.add(c['code']);v=cents(c['original_amount']);previous=(v*before*2+original)//(2*original);current=(v*after*2+original)//(2*original);delta=current-previous
            if cents(c['previous_amount'])!=previous or cents(c['new_amount'])!=current or cents(c['delta_amount'])!=delta or c['kind']=='OUTPUT_TAX' and v:raise ValueError('Component cumulative rounding differs.')
            if delta:uuid(c['account_id']);line(c['account_id'],delta,c['kind']=='WITHHOLDING',c['kind'])
            if c['kind']=='WITHHOLDING':ret+=delta;orig_ret+=v;new_ret+=current
            else:tax+=delta;orig_tax+=v;new_tax+=current
        if after+new_tax-new_ret>original+orig_tax-orig_ret or after+new_tax-new_ret<0:raise ValueError('Original concept settlement capacity exceeded.')
        values={'net':net,'tax':tax,'withholding':ret,'gross':net+tax,'settlement':net+tax-ret}
        if money_totals(a['totals'])!=values:raise ValueError('Concept tax totals differ.')
        for k in total:total[k]+=values[k]
    if money_totals(p['totals'])!=total:raise ValueError('Return aggregate differs.')
    lines=p['lines']
    if total['settlement']:
        if not lines:raise ValueError('Settlement missing.')
        settle=lines[-1];uuid(settle['account_id']);expected.append({'account_id':settle['account_id'],'debit':fmt(total['settlement']),'credit':'0.00','kind':'SETTLEMENT'})
    if lines!=expected:raise ValueError('Return journal differs from concepts.')

def validate(operation,data,payload,context):
    if data.get('company_id')!=context['tenant_id'] or data.get('invoice_id')!=payload['invoice_id'] or any(data.get(k) is not False for k in ('money_transferred','regulatory_verified','fiscal_document_created')):raise ValueError('Foreign or overstated return result.')
    positive(data['invoice_id'])
    if operation.startswith('review_'):
        uuid(data['review_id']);p=data['preview']
        if data['ledger_written'] is not False or p['company_id']!=context['tenant_id'] or p['provider_id']!=context['provider_id'] or p['reviewed_by']!=context['ledger_actor_id'] or p['invoice_id']!=payload['invoice_id'] or data['return_id']!=payload['return_id'] or p['return_id']!=payload['return_id']:raise ValueError('Review source/owner differs.')
        uuid(p['original_journal_id']);uuid(p['period_id'])
        if operation=='review_purchase_item_return':
            if p['revision']!=payload['expected_revision']+1 or any(p[k]!=payload[k] for k in ('entry_date','document_digest','evidence_digest')):raise ValueError('Review differs from requested return.')
            allocations(p,payload['selection'])
        else:
            if p['revision']!=payload['expected_revision'] or any(p[k]!=payload[k] for k in ('request_id','reason_code','entry_date','evidence_digest')):raise ValueError('Correction differs from request.')
            money_totals(p['totals'])
            if sum(cents(l['debit']) for l in p['lines'])!=sum(cents(l['credit']) for l in p['lines']):raise ValueError('Correction not balanced.')
        return
    if data.get('schema')!='sgacd-purchase-item-returns-v1' or data.get('currency')!='COP' or data.get('confirmations_restored') is not False or type(data.get('original_reversed')) is not bool:raise ValueError('Invalid capacity state.')
    uuid(data['document_id']);uuid(data['original_journal_id'])
    if not isinstance(data['items'],list) or not 2<=len(data['items'])<=20 or not isinstance(data['returns'],list) or len(data['returns'])>30 or type(data['revision']) is not int or data['revision']!=len(data['returns']):raise ValueError('Bounded return history required.')
    ids=set();used={};head_rows=[]
    for item in data['items']:
        if set(item)!={'item_id','basis_account_id','tax_category','policy_code','policy_revision','available_net','original','returned','remaining'}:raise ValueError('Unexpected capacity fields.')
        uuid(item['item_id']);uuid(item['basis_account_id'])
        if item['item_id'] in ids:raise ValueError('Duplicate capacity concept.')
        ids.add(item['item_id']);original=money_totals(item['original']);returned=money_totals(item['returned']);remaining=money_totals(item['remaining'])
        if any(original[k]-returned[k]!=remaining[k] for k in FIELDS) or cents(item['available_net'])!=(0 if data['original_reversed'] else remaining['net']):raise ValueError('Invalid remaining capacity.')
        used[item['item_id']]=returned['net']
    consumed={k:0 for k in ids};seen=set()
    for i,e in enumerate(data['returns'],1):
        for k in ('return_id','review_id','journal_id'):uuid(e[k])
        if e['return_id'] in seen or e['revision']!=i:raise ValueError('Return history reordered or duplicated.')
        seen.add(e['return_id']);money_totals(e['totals'])
        if not e.get('reversed'):
            for s in e['selection']:
                if set(s)!={'item_id','net'} or s['item_id'] not in consumed:raise ValueError('Unknown returned concept.')
                consumed[s['item_id']]+=cents(s['net'])
        else:uuid(e['reversal_journal_id'])
    if consumed!=used or data['original_reversed'] and any(used.values()):raise ValueError('History does not match effective capacity.')
    if operation=='purchase_item_return_state':
        if data.get('ledger_written') is not False or data.get('read_only') is not True:raise ValueError('Read cannot post.')
    else:
        uuid(data['journal_id'])
        if data.get('ledger_written') is not True or type(data.get('replayed')) is not bool:raise ValueError('Posting evidence missing.')
        if not any(e['journal_id']==data['journal_id'] or e.get('reversal_journal_id')==data['journal_id'] for e in data['returns']):raise ValueError('Returned journal missing from history.')
