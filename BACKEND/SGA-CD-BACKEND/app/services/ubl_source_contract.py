"""Bounded, read-only commercial source at the corporate trust boundary."""
import hashlib
import json
import re
from uuid import UUID


def validate(data, company_id, parameters):
    if not isinstance(parameters,dict) or set(parameters) not in ({'reservation_id','review_id'},{'opportunity_id','review_id'}):raise ValueError('Exact source reference required.')
    source_key='opportunity_id' if 'opportunity_id' in parameters else 'reservation_id'
    source_type='crm_opportunity' if source_key=='opportunity_id' else 'reservation'
    source_state='WON' if source_key=='opportunity_id' else 'CONFIRMED'
    fields = {'schema','company_id','review_id','source_fingerprint','intent_digest','snapshot',
              'read_only','ledger_written','fiscal_accepted','legal_tax_policy_verified','identity_independently_verified'}
    if not isinstance(data, dict) or set(data) != fields or data['schema'] != 'sgacd-reviewed-ubl-source-v1':
        raise ValueError('Invalid source shape.')
    if data['company_id'] != company_id or data['review_id'] != parameters['review_id'] or data['read_only'] is not True:
        raise ValueError('Foreign source.')
    for key in ('company_id','review_id'):
        if not isinstance(data[key], str) or str(UUID(data[key])) != data[key]: raise ValueError('Canonical identifier required.')
    if any(data[k] is not False for k in ('ledger_written','fiscal_accepted','legal_tax_policy_verified','identity_independently_verified')):
        raise ValueError('Unsupported authority.')
    for key in ('source_fingerprint','intent_digest'):
        if not isinstance(data[key],str) or not re.fullmatch('[0-9a-f]{64}',data[key]): raise ValueError('Invalid digest.')
    source=data['snapshot']
    if not isinstance(source,dict) or set(source)!={'schema','company_id','source_type','source_id','revision','state','currency','items','totals'}:
        raise ValueError('Invalid snapshot.')
    if source['schema']!='sgacd-invoice-intent-v1' or source['company_id']!=company_id or source['source_type']!=source_type or source['source_id']!=parameters[source_key] or source['state']!=source_state or source['currency']!='COP' or type(source['revision']) is not int or not 1<=source['revision']<=2147483647:
        raise ValueError('Unsupported snapshot context.')
    if str(UUID(source['source_id']))!=source['source_id']: raise ValueError('Canonical source required.')
    items=source['items']; seen=set(); net=tax=0
    def cents(value):
        if not isinstance(value,str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,13})\.[0-9]{2}',value):raise ValueError('Exact money required.')
        return int(value.replace('.',''))
    if not isinstance(items,list) or not 1<=len(items)<=100:raise ValueError('Bounded items required.')
    for item in items:
        if not isinstance(item,dict) or set(item)!={'item_id','net','tax','tax_category','policy_reference'}:raise ValueError('Invalid item.')
        uid=item['item_id']
        if not isinstance(uid,str) or str(UUID(uid))!=uid or uid in seen:raise ValueError('Duplicate item.')
        seen.add(uid); n=cents(item['net']); t=cents(item['tax'])
        if n<=0 or item['tax_category'] not in ('TAXABLE','EXEMPT','EXCLUDED') or item['tax_category']!='TAXABLE' and t!=0:raise ValueError('Invalid tax category.')
        if not isinstance(item['policy_reference'],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}',item['policy_reference']):raise ValueError('Policy reference required.')
        net+=n;tax+=t
    if [x['item_id'] for x in items]!=sorted(seen):raise ValueError('Noncanonical item order.')
    if not isinstance(source['totals'],dict) or set(source['totals'])!={'net','tax','gross'} or any(cents(source['totals'][k])!=v for k,v in [('net',net),('tax',tax),('gross',net+tax)]):raise ValueError('Totals differ.')
    if hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=data['intent_digest']:raise ValueError('Snapshot digest differs.')
    return data
