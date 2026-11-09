"""Pure bounded validation before forwarding a financial register across systems."""
from decimal import Decimal,localcontext
from datetime import date
import re
from uuid import UUID

KINDS={'INPUT_TAX','OUTPUT_TAX','WITHHOLDING'}
TOP={'schema','company_id','tenant_id','account_id','account_code','account_type','normal_side','since','until','currency','read_only','posted_only','valuation','debit','credit','normal_movement','attributed_normal_movement','tax_by_kind','unattributed_normal_movement','unattributed_journals','lines','ledger_written','dian_compared','fiscal_accepted','regulatory_verified','scope'}
LINE={'journal_id','date','journal_hash','is_reversal','debit','credit','normal_movement','tax_by_kind','unattributed_normal_movement','classification','document_id','reservation_id'}

def amount(value):
    if not isinstance(value,str) or not re.fullmatch(r'-?[0-9]{1,26}\.[0-9]{2}',value):raise ValueError('Exact monetary string required.')
    return Decimal(value)

def uuid(value):
    if not isinstance(value,str) or str(UUID(value))!=value:raise ValueError('Canonical UUID required.')

def kinds(value):
    if not isinstance(value,dict) or set(value)!=KINDS:raise ValueError('Exact tax kinds required.')
    return {k:amount(v) for k,v in value.items()}

def validate(data,*,company_id,account_id,since,until):
    if not isinstance(data,dict) or set(data)!=TOP:raise ValueError('Unexpected financial response fields.')
    if data['schema']!='sgacd-tax-register-v2' or data['company_id']!=company_id or data['tenant_id']!=company_id or data['account_id']!=account_id or data['since']!=since or data['until']!=until or data['currency']!='COP' or data['valuation']!='base_currency' or data['scope']!='SELECTED_ACCOUNT_MOVEMENTS_NOT_A_TAX_RETURN':raise ValueError('Financial response context mismatch.')
    uuid(data['company_id']);uuid(data['account_id'])
    if data['account_type'] not in {'ASSET','LIABILITY'} or data['normal_side']!=('DEBIT' if data['account_type']=='ASSET' else 'CREDIT') or not isinstance(data['account_code'],str) or not 1<=len(data['account_code'])<=64:raise ValueError('Account nature mismatch.')
    if any(data[k] is not True for k in ['read_only','posted_only']) or any(data[k] is not False for k in ['ledger_written','dian_compared','fiscal_accepted','regulatory_verified']):raise ValueError('Unsupported financial status.')
    if not isinstance(data['lines'],list) or len(data['lines'])>250 or type(data['unattributed_journals']) is not int:raise ValueError('Bounded register required.')
    with localcontext() as context:
        context.prec=64
        factor=Decimal(1) if data['normal_side']=='DEBIT' else Decimal(-1)
        totals={k:Decimal(0) for k in KINDS};left=right=unattributed=Decimal(0);seen=set();unknown=0
        for row in data['lines']:
            if not isinstance(row,dict) or set(row)!=LINE:raise ValueError('Unexpected movement fields.')
            uuid(row['journal_id'])
            if row['journal_id'] in seen or not isinstance(row['date'],str) or not since<=row['date']<=until or not isinstance(row['journal_hash'],str) or not re.fullmatch('[0-9a-f]{64}',row['journal_hash']) or type(row['is_reversal']) is not bool:raise ValueError('Movement identity/integrity mismatch.')
            if date.fromisoformat(row['date']).isoformat()!=row['date']:raise ValueError('Canonical movement date required.')
            seen.add(row['journal_id']);debit,credit=amount(row['debit']),amount(row['credit']);tax=kinds(row['tax_by_kind']);normal=amount(row['normal_movement']);unlinked=amount(row['unattributed_normal_movement'])
            if debit<0 or credit<0 or normal!=(debit-credit)*factor or normal!=sum(tax.values(),Decimal(0))+unlinked:raise ValueError('Movement totals do not reconcile.')
            source={'REVIEWED_COMMERCIAL_TAX':'document_id','REVIEWED_RESERVATION_TAX':'reservation_id','UNATTRIBUTED_REQUIRES_REVIEW':None}
            if row['classification'] not in source:raise ValueError('Unknown source classification.')
            expected=source[row['classification']]
            for field in ['document_id','reservation_id']:
                if field==expected:uuid(row[field])
                elif row[field] is not None:raise ValueError('Unexpected source identity.')
            if expected is None and any(tax.values()):raise ValueError('Unattributed movement cannot claim tax attribution.')
            left+=debit;right+=credit;unattributed+=unlinked;unknown+=bool(unlinked or expected is None)
            for kind in KINDS:totals[kind]+=tax[kind]
        if amount(data['debit'])!=left or amount(data['credit'])!=right or kinds(data['tax_by_kind'])!=totals or amount(data['normal_movement'])!=(left-right)*factor or amount(data['attributed_normal_movement'])!=sum(totals.values(),Decimal(0)) or amount(data['unattributed_normal_movement'])!=unattributed or data['unattributed_journals']!=unknown:raise ValueError('Register totals do not reconcile.')
    return data
