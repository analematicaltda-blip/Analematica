"""Exact signed settlement result, requested receipt, scope and posting qualification."""
from decimal import Decimal,ROUND_HALF_UP,localcontext
from datetime import date
import re
from .reviewed_fx_contract import identifier,digest,amount
from .fx_revaluation_contract import signed,source_totals

def preview(b,context):
    if b['company_id']!=context['tenant_id'] or b['reviewed_by']!=context['ledger_actor_id'] or b['classification']!='MONETARY_DECLARED':raise ValueError('Settlement scope/classification changed.')
    for k in ['request_id','period_id','gain_account_id','loss_account_id']:identifier(b[k])
    digest(b['evidence_digest']);s=b['source'];c=b['cash'];p=b['calculation'];t=b['terms']
    identifier(s['account_id']);identifier(c['cash_line_id']);identifier(c['cash_account_id']);identifier(c['clearing_account_id']);identifier(c['journal_id']);digest(c['journal_hash'])
    if len({s['account_id'],c['cash_account_id'],c['clearing_account_id'],b['gain_account_id'],b['loss_account_id']})!=5 or s['currency'] not in {'USD','EUR'} or s['as_of']!=c['date'] or t['base_currency']!=s['currency'] or t['target_currency']!='COP':raise ValueError('Distinct accounts, date and currency required.')
    if set(t)!={'base_currency','target_currency','rate','source_reference','source_version','observed_at','valid_from','valid_until','evidence_digest'} or not isinstance(t['rate'],str) or not re.fullmatch(r'(0|[1-9][0-9]{0,8})[.][0-9]{6}',t['rate']) or Decimal(t['rate'])<=0 or not date.fromisoformat(t['valid_from'])<=date.fromisoformat(s['as_of'])<=date.fromisoformat(t['valid_until']):raise ValueError('Canonical rate covering settlement date required.')
    digest(t['evidence_digest'])
    qty=amount(b['quantity']);foreign,carrying=source_totals(s);asset=foreign>0
    if qty<=0 or qty>abs(foreign) or not foreign or (foreign>0)!=(carrying>0) or c['direction']!=('IN' if asset else 'OUT'):raise ValueError('Invalid source balance/receipt direction.')
    with localcontext() as ctx:
        ctx.prec=38;book=abs(carrying) if qty==abs(foreign) else (abs(carrying)*qty/abs(foreign)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP);cash=(qty*Decimal(t['rate'])).quantize(Decimal('.01'),rounding=ROUND_HALF_UP);gain=(cash-book)*(1 if asset else -1);gain=gain if gain else Decimal('0.00');remaining=abs(foreign)-qty;remaining_cop=abs(carrying)-book
    if cash<=0 or book<=0 or format(cash,'.2f')!=c['amount_cop']:raise ValueError('Receipt does not match declared FX quantity/rate.')
    lines=[{'account_id':s['account_id'],'debit':'0.00' if asset else format(book,'.2f'),'credit':format(book,'.2f') if asset else '0.00'},{'account_id':c['clearing_account_id'],'debit':format(cash,'.2f') if asset else '0.00','credit':'0.00' if asset else format(cash,'.2f')}]
    if gain:lines.append({'account_id':b['gain_account_id'] if gain>0 else b['loss_account_id'],'debit':format(abs(gain),'.2f') if gain<0 else '0.00','credit':format(gain,'.2f') if gain>0 else '0.00'})
    expected={'quantity':format(qty,'.2f'),'carrying_released_cop':format(book,'.2f'),'cash_cop':format(cash,'.2f'),'realized_difference_cop':format(gain,'.2f'),'foreign_delta':format(-qty if asset else qty,'.2f'),'remaining_foreign':format(remaining if asset or not remaining else -remaining,'.2f'),'remaining_cop':format(remaining_cop if asset or not remaining_cop else -remaining_cop,'.2f'),'rounding':'PROPORTIONAL_CARRYING_HALF_UP_FINAL_REMAINDER','lines':lines}
    if p!=expected:raise ValueError('Settlement carrying/difference/remaining/lines changed.')
    return b

def validate(operation,data,payload,context):
    if data.get('company_id')!=context['tenant_id'] or any(data.get(k) is not False for k in ['money_transferred','bank_verified','rate_independently_verified']):raise ValueError('Settlement scope/authenticity overstated.')
    if operation=='fx_settlement_request_state':
        if data.get('schema')!='sgacd-fx-settlement-request-state-v1' or data.get('request_id')!=payload['request_id'] or type(data.get('found')) is not bool or data.get('read_only') is not True or data.get('confirmations_restored') is not False or data.get('ledger_written') is not False:raise ValueError('Settlement request recovery changed.')
        if data['found']:
            if data['state']['preview']['request_id']!=payload['request_id']:raise ValueError('Different recovered settlement request.')
            validate('fx_settlement_state',data['state'],{'review_id':data['state']['review_id']},context)
        elif 'state' in data:raise ValueError('Missing request cannot restore a review.')
        return
    if operation=='fx_settlement_catalog':
        if data.get('schema')!='sgacd-fx-settlement-catalog-v1' or data.get('read_only') is not True or data.get('ledger_written') is not False or type(data.get('truncated')) is not bool or set(data['accounts'])!={'monetary','clearing','gains','losses'} or len(data['recorded_cash'])>50:raise ValueError('Bounded read-only source catalog required.')
        for records in data['accounts'].values():
            if len(records)>100:raise ValueError('Unbounded account catalog.')
            for r in records:identifier(r['id'])
        for r in data['recorded_cash']:
            for k in ['cash_line_id','cash_account_id','clearing_account_id','journal_id']:identifier(r[k])
            digest(r['journal_hash']);amount(r['amount_cop'])
        return
    identifier(data['review_id'])
    if operation=='post_fx_settlement':
        if data.get('schema')!='sgacd-fx-settlement-result-v1' or data['review_id']!=payload['review_id'] or data.get('ledger_written') is not True or data.get('fiscal_accepted') is not False or any(type(data.get(k)) is not bool for k in ['source_current','original_reversed','replayed']):raise ValueError('Settlement posting qualification changed.')
        for k in ['journal_id','account_id','cash_line_id']:identifier(data[k])
        digest(data['journal_hash'])
        for k in ['quantity','carrying_released_cop','cash_cop']:amount(data[k])
        for k in ['realized_difference_cop','remaining_foreign','remaining_cop']:signed(data[k])
        if data.get('monetary_kind') not in {'ASSET','LIABILITY'}:raise ValueError('Explicit settlement monetary kind required.')
        factor=1 if data['monetary_kind']=='ASSET' else -1
        if signed(data['realized_difference_cop'])!=(amount(data['cash_cop'])-amount(data['carrying_released_cop']))*factor or signed(data['remaining_foreign'])*factor<0 or signed(data['remaining_cop'])*factor<0:raise ValueError('Posted cash, released carrying and realized difference do not reconcile.')
        return
    b=preview(data['preview'],context)
    if data.get('ledger_written') is not False or type(data.get('source_current')) is not bool:raise ValueError('Settlement preview must not post.')
    if operation=='review_fx_settlement':
        if any(b[k]!=payload[k] for k in ['request_id','quantity','terms','gain_account_id','loss_account_id','evidence_digest']) or any(b['source'][k]!=payload[k] for k in ['account_id','currency','as_of']) or any(b['cash'][k]!=payload[k] for k in ['cash_line_id','clearing_account_id']):raise ValueError('Requested settlement changed.')
    else:
        if data['review_id']!=payload['review_id'] or data.get('read_only') is not True or data.get('confirmations_restored') is not False:raise ValueError('Recovered settlement contract changed.')
        if data.get('applied') is not None:
            validate('post_fx_settlement',data['applied'],{'review_id':data['review_id']},context)
            if any(data['applied'][k]!=b['calculation'][k] for k in ['quantity','carrying_released_cop','cash_cop','realized_difference_cop','remaining_foreign','remaining_cop']) or data['applied']['cash_line_id']!=b['cash']['cash_line_id'] or data['applied']['account_id']!=b['source']['account_id']:raise ValueError('Recovered settlement differs from review.')
