"""Explain original declared policy versions without recomputing fiscal obligations.

For a return, references describe the original document: its amount is NOT the
return amount. Register movements retain their independently verified contra lines.
"""
from .exceptions import AccountingError
from . import tax_policies

def references(company,body,cache):
    origin=body.get('tax_source',body)
    if 'fact' not in origin:return []
    fact=origin['fact'];quotes={row['item_id']:row for row in origin['preview']['quotes']};result=[]
    for item in fact['items']:
        quote=quotes.get(item['item_id'])
        if quote is None:raise AccountingError('Tax policy quotation provenance missing.')
        key=(item['policy_code'],item['policy_revision'])
        if key not in cache:
            row=tax_policies.versions(company.pk,key[0]).filter(payload__revision=key[1]).first()
            if row is None:raise AccountingError('Original tax policy version unavailable.')
            policy=tax_policies.verified(row,company.pk)
            cache[key]=(row,policy)
        row,policy=cache[key];terms=policy['terms']
        if quote['policy_id']!=str(row.pk) or quote['policy_digest']!=row.payload['policy_digest'] or not terms['valid_from']<=fact['entry_date']<=terms['valid_until']:raise AccountingError('Original tax policy quotation changed or outside validity.')
        result.append({'item_id':item['item_id'],'policy_id':str(row.pk),'code':terms['code'],'revision':policy['revision'],'policy_digest':row.payload['policy_digest'],'valid_from':terms['valid_from'],'valid_until':terms['valid_until'],'evidence_digest':policy['evidence_digest'],'tax_category':item['tax_category'],'direction':fact['direction'],'economic_date':fact['entry_date'],'reference_basis':'ORIGINAL_DOCUMENT_POLICY_NOT_ADJUSTMENT_AMOUNT'})
    return result
