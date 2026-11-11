"""Conserve signed monetary balance, historical base, and proposed adjustment."""
from decimal import Decimal,ROUND_HALF_UP,localcontext
from datetime import date
import re
from .reviewed_fx_contract import identifier,digest,amount

def signed(value):
    if not isinstance(value,str) or not re.fullmatch(r'-?(?:0|[1-9][0-9]{0,15})\.[0-9]{2}',value) or value=='-0.00':raise ValueError('Exact signed balance required.')
    return Decimal(value)

def source_totals(source):
    day=date.fromisoformat(source['as_of'])
    records=source['records'];seen=[];foreign=carrying=Decimal(0)
    if not isinstance(records,list) or not 1<=len(records)<=50:raise ValueError('Bounded monetary history required.')
    with localcontext() as ctx:
        ctx.prec=38
        for r in records:
            if not isinstance(r,dict) or set(r) not in ({'line_id','journal_id','journal_hash','date','currency','debit','credit','amount_base','rate'},{'line_id','journal_id','journal_hash','date','currency','debit','credit','amount_base','rate','foreign_delta','settlement_review_id','settlement_proof_digest'}) or r['currency'] not in ('COP',source['currency']) or date.fromisoformat(r['date'])>day:raise ValueError('Invalid historical monetary line.')
            identifier(r['line_id']);identifier(r['journal_id']);digest(r['journal_hash']);seen.append(r['line_id']);left=amount(r['debit']);right=amount(r['credit']);base=amount(r['amount_base'])
            if (left>0)==(right>0) or not isinstance(r['rate'],str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,11})\.[0-9]{6}',r['rate']) or Decimal(r['rate'])<=0:raise ValueError('Invalid historical sides/rate.')
            val=left or right;sign=1 if left else -1
            if (val*Decimal(r['rate'])).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)!=base or r['currency']=='COP' and Decimal(r['rate'])!=1:raise ValueError('Historical COP conversion differs.')
            if r['currency']==source['currency']:foreign+=sign*val
            if 'foreign_delta' in r:
                identifier(r['settlement_review_id']);digest(r['settlement_proof_digest'])
                if r['currency']!='COP' or not signed(r['foreign_delta']):raise ValueError('Explicit COP settlement foreign-quantity provenance required.')
                foreign+=signed(r['foreign_delta'])
            carrying+=sign*base
        if seen!=sorted(set(seen)) or foreign!=signed(source['foreign_balance']) or carrying!=signed(source['carrying_cop']):raise ValueError('Monetary balance does not match records.')
    return foreign,carrying

def preview(body,company_id,actor_id):
    keys={'company_id','request_id','reviewed_by','period_id','source','terms','gain_account_id','loss_account_id','classification','classification_independently_verified','calculation'}
    if not isinstance(body,dict) or set(body)!=keys or body['company_id']!=company_id or body['reviewed_by']!=actor_id or body['classification']!='MONETARY_DECLARED' or body['classification_independently_verified'] is not False:raise ValueError('Foreign or overstated FX revaluation.')
    for k in ('request_id','period_id','gain_account_id','loss_account_id'):identifier(body[k])
    source=body['source'];terms=body['terms']
    if not isinstance(source,dict) or set(source)!={'account_id','currency','as_of','foreign_balance','carrying_cop','records'} or source['currency'] not in ('USD','EUR'):raise ValueError('Invalid monetary source.')
    identifier(source['account_id']);day=date.fromisoformat(source['as_of'])
    if day.isoformat()!=source['as_of'] or len({source['account_id'],body['gain_account_id'],body['loss_account_id']})!=3:raise ValueError('Invalid FX date/mapping.')
    if not isinstance(terms,dict) or set(terms)!={'base_currency','target_currency','rate','source_reference','source_version','observed_at','valid_from','valid_until','evidence_digest'} or terms['base_currency']!=source['currency'] or terms['target_currency']!='COP' or not isinstance(terms['rate'],str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,8})\.[0-9]{6}',terms['rate']) or Decimal(terms['rate'])<=0:raise ValueError('Invalid revaluation quote.')
    digest(terms['evidence_digest'])
    if not date.fromisoformat(terms['valid_from'])<=day<=date.fromisoformat(terms['valid_until']):raise ValueError('Quote does not cover FX date.')
    with localcontext() as ctx:
        ctx.prec=38
        foreign,carrying=source_totals(source)
        desired=(foreign*Decimal(terms['rate'])).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP);delta=desired-carrying;value=format(abs(delta),'.2f');counter=body['gain_account_id'] if delta>0 else body['loss_account_id']
    expected={'desired_cop':format(desired,'.2f'),'difference_cop':format(delta,'.2f'),'rounding':'BALANCE_HALF_UP','lines':[{'account_id':source['account_id'],'debit':value if delta>0 else '0.00','credit':value if delta<0 else '0.00'},{'account_id':counter,'debit':value if delta<0 else '0.00','credit':value if delta>0 else '0.00'}]}
    if not delta or body['calculation']!=expected:raise ValueError('FX adjustment does not reconcile exactly.')
    return body

def posted(data,company_id,review_id):
    fields={'schema','company_id','review_id','journal_id','journal_hash','account_id','foreign_balance','carrying_cop','desired_cop','difference_cop','source_current','original_reversed','replayed','ledger_written','money_transferred','rate_independently_verified','fiscal_accepted'}
    if not isinstance(data,dict) or set(data)!=fields or data['schema']!='sgacd-fx-revaluation-result-v1' or data['company_id']!=company_id or data['review_id']!=review_id or data['ledger_written'] is not True or any(data[k] is not False for k in ('money_transferred','rate_independently_verified','fiscal_accepted')) or any(type(data[k]) is not bool for k in ('source_current','original_reversed','replayed')):raise ValueError('Invalid FX adjustment result.')
    for k in ('review_id','journal_id','account_id'):identifier(data[k])
    digest(data['journal_hash']);signed(data['foreign_balance'])
    if signed(data['carrying_cop'])+signed(data['difference_cop'])!=signed(data['desired_cop']) or signed(data['difference_cop'])==0:raise ValueError('FX result does not conserve balance.')

def validate(operation,data,payload,context):
    company_id=context['tenant_id']
    if not isinstance(data,dict) or data.get('company_id')!=company_id or data.get('money_transferred') is not False or data.get('rate_independently_verified') is not False:raise ValueError('Foreign/overstated FX operation.')
    if operation=='fx_revaluation_catalog':
        if set(data)!={'company_id','accounts','truncated','read_only','ledger_written','money_transferred','rate_independently_verified'} or data['read_only'] is not True or data['ledger_written'] is not False or type(data['truncated']) is not bool or set(data['accounts'])!={'monetary','gains','losses'}:raise ValueError('Invalid FX catalog.')
        for key,kinds in [('monetary',{'ASSET','LIABILITY'}),('gains',{'REVENUE'}),('losses',{'EXPENSE'})]:
            rows=data['accounts'][key]
            if not isinstance(rows,list) or len(rows)>100 or len({r['id'] for r in rows})!=len(rows):raise ValueError('Unbounded/duplicate FX accounts.')
            for r in rows:
                if set(r)!={'id','code','name','type'} or r['type'] not in kinds:raise ValueError('Invalid FX account type.')
                identifier(r['id'])
    elif operation=='post_fx_revaluation':posted(data,company_id,payload['review_id'])
    else:
        identifier(data['review_id']);body=preview(data['preview'],company_id,context['ledger_actor_id'])
        if operation=='review_fx_revaluation':
            if set(data)!={'company_id','review_id','preview','ledger_written','money_transferred','rate_independently_verified'} or data['ledger_written'] is not False or any(body[k]!=payload[k] for k in ('request_id','terms','gain_account_id','loss_account_id')) or any(body['source'][k]!=payload[k] for k in ('account_id','currency','as_of')):raise ValueError('FX proposal differs from request.')
        else:
            if set(data)!={'company_id','review_id','preview','source_current','applied','read_only','confirmations_restored','ledger_written','money_transferred','rate_independently_verified'} or data['review_id']!=payload['review_id'] or data['read_only'] is not True or data['confirmations_restored'] is not False or data['ledger_written'] is not False or type(data['source_current']) is not bool:raise ValueError('Invalid recovered FX state.')
            if data['applied'] is not None:
                posted(data['applied'],company_id,data['review_id'])
                if any(data['applied'][k]!=body['source'][k] for k in ('account_id','foreign_balance','carrying_cop')) or any(data['applied'][k]!=body['calculation'][k] for k in ('desired_cop','difference_cop')):raise ValueError('Recovered FX posting differs from review.')
