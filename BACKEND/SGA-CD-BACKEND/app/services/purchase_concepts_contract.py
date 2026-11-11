"""Conserve persisted concept inputs, component taxes, account roles and totals."""
import re
from uuid import UUID

def uid(v):
    if not isinstance(v,str) or str(UUID(v))!=v:raise ValueError('Canonical concept identifier required.')
def cents(v):
    if not isinstance(v,str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,17})\.[0-9]{2}',v):raise ValueError('Exact concept amount required.')
    return int(v.replace('.',''))
def fmt(v):return f'{v//100}.{v%100:02d}'

def validate(inputs,preview,revision):
    if not isinstance(inputs,dict) or set(inputs)!={'selection','settlement_account_id','revision'} or type(revision) is not int or type(inputs['revision']) is not int or inputs['revision']!=revision or revision<1:raise ValueError('Invalid recovered concept form.')
    uid(inputs['settlement_account_id']);items=inputs['selection']
    if not isinstance(items,list) or not 1<=len(items)<=20 or not isinstance(preview,dict) or len(preview.get('quotes',[]))!=len(items):raise ValueError('Bounded concept/quote correspondence required.')
    if preview.get('currency')!='COP' or preview.get('regulatory_verified') is not False or preview.get('source_independently_verified') is not False:raise ValueError('Unsupported concept authority/currency.')
    seen=set();net_total=tax_total=ret_total=0;expected=[]
    def line(account,amount,debit,kind):
        if amount:expected.append({'account_id':account,'debit':fmt(amount if debit else 0),'credit':fmt(0 if debit else amount),'kind':kind})
    for item,quote in zip(items,preview['quotes']):
        if not isinstance(item,dict) or set(item)!={'item_id','net','tax_category','policy_code','policy_revision','basis_account_id','tax_accounts'}:raise ValueError('Unexpected concept fields.')
        uid(item['item_id']);uid(item['basis_account_id']);net=cents(item['net'])
        if item['item_id'] in seen or net<=0 or item['tax_category'] not in ('TAXABLE','EXEMPT','EXCLUDED') or not isinstance(item['policy_code'],str) or not re.fullmatch(r'[A-Z0-9][A-Z0-9_-]{0,39}',item['policy_code']) or type(item['policy_revision']) is not int or item['policy_revision']<1 or not isinstance(item['tax_accounts'],dict):raise ValueError('Invalid concept identity/policy.')
        seen.add(item['item_id'])
        if not isinstance(quote,dict) or set(quote)!={'item_id','policy_id','policy_digest','components'} or quote['item_id']!=item['item_id']:raise ValueError('Concept quote order/identity differs.')
        uid(quote['policy_id'])
        if not isinstance(quote['policy_digest'],str) or not re.fullmatch('[a-f0-9]{64}',quote['policy_digest']) or not isinstance(quote['components'],list) or len(quote['components'])>20:raise ValueError('Invalid quote provenance.')
        line(item['basis_account_id'],net,True,'BASIS');required=set();codes=set();tax=ret=0
        for component in quote['components']:
            if not isinstance(component,dict) or set(component)!={'code','kind','basis','rate_bps','applied','amount'} or component['kind'] not in ('INPUT_TAX','OUTPUT_TAX','WITHHOLDING') or type(component['applied']) is not bool or type(component['rate_bps']) is not int or not 0<=component['rate_bps']<=10000 or cents(component['basis'])!=net or component['code'] in codes:raise ValueError('Invalid tax component.')
            code=component['code'];codes.add(code)
            if not isinstance(code,str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,29}',code):raise ValueError('Invalid component code.')
            value=(net*component['rate_bps']+5000)//10000 if component['applied'] else 0
            if cents(component['amount'])!=value:raise ValueError('Component rounding differs.')
            if value:
                if component['kind']=='OUTPUT_TAX':raise ValueError('Positive output tax is not purchase input tax.')
                required.add(code);target=item['tax_accounts'].get(code);uid(target)
                if target in (item['basis_account_id'],inputs['settlement_account_id']):raise ValueError('Tax and basis/settlement roles collide.')
                line(target,value,component['kind']=='INPUT_TAX',component['kind'])
            if component['kind']!='WITHHOLDING':tax+=value
            else:ret+=value
        if required!=set(item['tax_accounts']) or ret>net+tax or item['basis_account_id']==inputs['settlement_account_id']:raise ValueError('Tax mapping differs from positive components.')
        net_total+=net;tax_total+=tax;ret_total+=ret
    line(inputs['settlement_account_id'],net_total+tax_total-ret_total,False,'SETTLEMENT')
    expected_totals={'net':fmt(net_total),'tax':fmt(tax_total),'withholding':fmt(ret_total),'gross':fmt(net_total+tax_total),'settlement':fmt(net_total+tax_total-ret_total)}
    if preview.get('lines')!=expected or preview.get('totals')!=expected_totals:raise ValueError('Concept journal or invoice totals differ.')
    return inputs
