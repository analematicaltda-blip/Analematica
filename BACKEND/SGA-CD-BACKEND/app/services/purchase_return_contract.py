"""Exact native return responses, never fiscal issuance or cash refunds."""
from decimal import Decimal
from .native_purchase_contract import positive,uuid
import re
KINDS={'net','tax','withholding','gross','settlement'}
def amounts(value):
    if not isinstance(value,dict) or set(value)!=KINDS or any(not isinstance(v,str) or not re.fullmatch(r'(0|[1-9][0-9]{0,11})[.][0-9]{2}',v) for v in value.values()):raise ValueError('Exact return amounts required.')
    result={k:Decimal(v) for k,v in value.items()}
    if result['net']+result['tax']!=result['gross'] or result['gross']-result['withholding']!=result['settlement']:raise ValueError('Return component arithmetic changed.')
    return result

def validate(operation,data,payload,context):
    if not isinstance(data,dict) or data.get('company_id')!=context['tenant_id'] or data.get('invoice_id')!=payload['invoice_id'] or any(data.get(k) is not False for k in ['money_transferred','fiscal_document_created','regulatory_verified']):raise ValueError('Return company/invoice/financial flags changed.')
    reviewing=operation in {'review_purchase_return','review_purchase_return_void'}
    voiding=operation=='review_purchase_return_void'
    common={'company_id','invoice_id','document_id','returns','revision','history_digest','returned','remaining','currency','money_transferred','fiscal_document_created','regulatory_verified','confirmations_restored','schema','native_source_verified','ledger_written'}
    expected={'company_id','invoice_id','return_id','review_id','preview','ledger_written','money_transferred','regulatory_verified','fiscal_document_created'} if reviewing else common|({'read_only','original_reversed'} if operation=='purchase_return_state' else {'journal_id','replayed'})
    if set(data)!=expected:raise ValueError('Unexpected return response fields.')
    positive(data['invoice_id'])
    if reviewing:
        if data.get('ledger_written') is not False or data.get('return_id')!=payload['return_id']:raise ValueError('Return review cannot post.')
        uuid(data['review_id']);p=data['preview'];a=amounts(p['totals'])
        if (not voiding and a['net']!=Decimal(payload['net_amount'])) or p['company_id']!=context['tenant_id'] or p['provider_id']!=context['provider_id'] or p['invoice_id']!=payload['invoice_id'] or p['return_id']!=payload['return_id'] or (not voiding and p['document_digest']!=payload['document_digest']) or p['entry_date']!=payload['entry_date']:raise ValueError('Return proposal changed.')
        expected_preview={'company_id','provider_id','invoice_id','document_id','return_id','revision','history_digest','original_journal_id','reviewed_by','entry_date','period_id','evidence_digest','totals','lines','expires_at'}|({'request_id','void_index','target_journal_id','target_proof_digest','reason_code'} if voiding else {'original_hash','document_digest'})
        if set(p)!=expected_preview:raise ValueError('Unexpected return preview fields.')
        if voiding and (p['request_id']!=payload['request_id'] or p['reason_code']!=payload['reason_code'] or p['evidence_digest']!=payload['evidence_digest']):raise ValueError('Correction proposal changed.')
        for row in p['lines']:
            if set(row)!={'account_id','kind','debit','credit'} or row['kind'] not in {'BASIS','INPUT_TAX','WITHHOLDING','SETTLEMENT'}:raise ValueError('Unexpected return component fields.')
            uuid(row['account_id'])
            for key in ['debit','credit']:
                if not isinstance(row[key],str) or not re.fullmatch(r'(0|[1-9][0-9]{0,11})[.][0-9]{2}',row[key]):raise ValueError('Exact contra amounts required.')
        if not isinstance(p['lines'],list) or len(p['lines'])>4 or sum(Decimal(r['debit']) for r in p['lines'])!=sum(Decimal(r['credit']) for r in p['lines']):raise ValueError('Return review must balance.')
        return
    if data.get('schema')!='sgacd-native-purchase-return-v1' or data.get('native_source_verified') is not True or data.get('currency')!='COP' or data.get('confirmations_restored') is not False:raise ValueError('Return source/status mismatch.')
    if not isinstance(data['history_digest'],str) or not re.fullmatch('[a-f0-9]{64}',data['history_digest']):raise ValueError('History digest required.')
    uuid(data['document_id']);returned=amounts(data['returned']);remaining=amounts(data['remaining']);rows=data['returns']
    if not isinstance(rows,list) or len(rows)>30 or type(data['revision']) is not int or data['revision']!=len(rows):raise ValueError('Bounded return history required.')
    sums={k:Decimal(0) for k in KINDS};seen=set()
    for n,row in enumerate(rows,1):
        fields={'return_id','journal_id','review_id','revision','totals','proof_digest'}
        if set(row) not in [fields,fields|{'reversed','reversal_journal_id','reversal_digest'}]:raise ValueError('Unexpected return history fields.')
        if 'reversed' in row:
            if row['reversed'] is not True or not isinstance(row['reversal_digest'],str) or not re.fullmatch('[a-f0-9]{64}',row['reversal_digest']):raise ValueError('Correction evidence missing.')
            uuid(row['reversal_journal_id'])
            if row['reversal_journal_id']==row['journal_id']:raise ValueError('Correction must preserve its original journal.')
        for key in ['return_id','journal_id','review_id']:uuid(row[key])
        if row['return_id'] in seen or type(row['revision']) is not int or row['revision']!=n or not isinstance(row['proof_digest'],str) or not re.fullmatch('[a-f0-9]{64}',row['proof_digest']):raise ValueError('Return history duplicated or changed.')
        seen.add(row['return_id']);a=amounts(row['totals'])
        if not row.get('reversed'):
            for k in sums:sums[k]+=a[k]
    if sums!=returned or remaining['net']==0 and any(remaining.values()):raise ValueError('Return history/capacity mismatch.')
    if operation=='purchase_return_state':
        if type(data.get('original_reversed')) is not bool or data.get('original_reversed') and (any(remaining.values()) or any(returned.values()) or any(not r.get('reversed') for r in rows)):raise ValueError('Full reversal cannot retain active return capacity.')
        if data.get('read_only') is not True or data.get('ledger_written') is not False:raise ValueError('Recovery cannot post.')
    else:
        if data.get('ledger_written') is not True or type(data.get('replayed')) is not bool or data.get('journal_id') not in {r.get('reversal_journal_id') if operation=='void_purchase_return' else r['journal_id'] for r in rows}:raise ValueError('Posted return has no matching history.')
