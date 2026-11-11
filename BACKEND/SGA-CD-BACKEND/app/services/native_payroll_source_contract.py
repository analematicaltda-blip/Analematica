"""Native payroll capture must agree with the requested source and never post money."""
import hashlib,json,re
from uuid import UUID

def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def validate(operation,data,payload,context):
    correction=operation=='correct_native_payroll_novelty'
    if data.get('schema')!='sgacd-native-payroll-source-v1' or data.get('company_id')!=context['tenant_id'] or data.get('payroll_id')!=str(UUID(payload['payroll_id'])) or (not correction and data.get('reference_digest')!=digest(payload['source_reference'])) or any(data.get(k) is not False for k in ['ledger_written','money_transferred','document_uploaded','authorization_independently_verified','confirmations_restored']):raise ValueError('Source capture scope/flags changed.')
    lookup=operation=='lookup_native_payroll_novelty'
    if data.get('read_only') is not lookup or type(data.get('found')) is not bool:raise ValueError('Source capture read contract changed.')
    if type(data.get('metadata_written')) is not bool or lookup and data['metadata_written']:raise ValueError('Read-only source lookup cannot write metadata.')
    if not data['found']:
        if not lookup or 'source' in data:raise ValueError('Source capture missing.')
        return
    if type(data.get('replayed')) is not bool or not lookup and data['metadata_written'] is not (not data['replayed']):raise ValueError('Capture/replay write qualification changed.')
    s=data['source']
    if type(data.get('novelty_id')) is not int or not 1<=data['novelty_id']<=9007199254740991 or s['novelty_id']!=data['novelty_id'] or s['payroll_id']!=data['payroll_id'] or s['concept_kind'] not in ['DEVENGADO','DEDUCCION'] or s['quantity']!='1.00' or type(data.get('processed')) is not bool or digest(s)!=data.get('source_digest'):raise ValueError('Source identity, amount or digest changed.')
    if not isinstance(s['amount'],str) or not re.fullmatch(r'(0|[1-9][0-9]{0,11})[.][0-9]{2}',s['amount']) or int(s['amount'].replace('.',''))<=0:raise ValueError('Positive exact source amount required.')
    for key in ['evidence_digest','authorization_digest']:
        if not isinstance(data.get(key),str) or not re.fullmatch('[0-9a-f]{64}',data[key]):raise ValueError('Source references required.')
    history=data.get('history');revision=data.get('revision')
    if type(revision) is not int or not 0<=revision<=20 or not isinstance(history,list) or len(history)!=revision or not isinstance(data.get('history_digest'),str) or not re.fullmatch('[0-9a-f]{64}',data['history_digest']):raise ValueError('Bounded source history required.')
    previous=None
    for number,b in enumerate(history,1):
        if not isinstance(b,dict) or b.get('company_id')!=context['tenant_id'] or b.get('payroll_id')!=data['payroll_id'] or b.get('novelty_id')!=data['novelty_id'] or b.get('revision')!=number or b.get('reason_code') not in {'DATA_ENTRY_ERROR','UPDATED_SUPPORT','SOURCE_REVIEW'}:raise ValueError('Source correction history scope changed.')
        if previous is not None and (b['previous_digest']!=digest(previous) or b['before']!=previous['after']):raise ValueError('Source correction chain changed.')
        if b['after']!={**b['before'],'date':b['after']['date'],'amount':b['after']['amount']}:raise ValueError('Source correction replaced immutable identity.')
        previous=b
    if history and (history[-1]['after']!=s or digest(history[-1])!=data['history_digest'] or any(history[-1][k]!=data[k] for k in ['evidence_digest','authorization_digest'])):raise ValueError('Effective source differs from correction history.')
    if correction:
        if data.get('correction_request_id')!=payload['request_id'] or data.get('revision')!=payload['expected_revision']+1 or not history or history[-1]['reason_code']!=payload['reason_code'] or data['novelty_id']!=payload['novelty_id'] or s['date']!=payload['event_date'] or s['amount']!=payload['amount'] or any(data[k]!=payload[k] for k in ['evidence_digest','authorization_digest']):raise ValueError('Requested source correction changed.')
    if not lookup and not correction and (data['request_id']!=payload['request_id'] or s['employee_id']!=payload['employee_id'] or s['concept_id']!=payload['concept_id'] or s['date']!=payload['event_date'] or s['amount']!=payload['amount'] or any(data[k]!=payload[k] for k in ['evidence_digest','authorization_digest'])):raise ValueError('Requested source data changed.')
