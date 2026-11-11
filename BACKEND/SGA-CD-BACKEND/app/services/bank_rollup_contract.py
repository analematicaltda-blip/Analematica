"""Cross-backend consolidation results: scope, exact arithmetic and no payments."""
import hashlib,json,re
from uuid import UUID

def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def identifier(value):
    if not isinstance(value,str) or str(UUID(value))!=value:raise ValueError('Canonical identity required.')
def validate(operation,data,payload,context):
    if data.get('company_id')!=context['tenant_id'] or any(data.get(k) is not False for k in ['ledger_written','money_transferred','bank_verified','confirmations_restored']):raise ValueError('Period consolidation scope or financial flags changed.')
    identifier(data['account_id'])
    if 'account_id' in payload and data['account_id']!=payload['account_id']:raise ValueError('Different cash account returned.')
    if operation=='bank_rollup_sources':
        if data.get('schema')!='sgacd-bank-rollup-sources-v1' or data.get('read_only') is not True or type(data.get('truncated')) is not bool or not isinstance(data.get('batches'),list) or len(data['batches'])>50:raise ValueError('Bounded read-only batch catalog required.')
        seen=set()
        for row in data['batches']:
            identifier(row['reconciliation_id']);identifier(row['statement_id'])
            if row['reconciliation_id'] in seen or type(row['source_current']) is not bool:raise ValueError('Duplicate or unqualified batch.')
            seen.add(row['reconciliation_id'])
        return
    if operation=='bank_rollup_state':
        if data.get('schema')!='sgacd-bank-rollup-state-v1' or data.get('read_only') is not True or data.get('since')!=payload['since'] or data.get('until')!=payload['until'] or type(data.get('revision')) is not int or data['revision']<0:raise ValueError('Different consolidation state returned.')
        if data.get('preview') is not None:preview(data['preview'],data,context)
        elif data['revision']!=0 or data.get('review_id') is not None or data.get('applied') is not None:raise ValueError('Missing consolidation history.')
        if data.get('applied') is not None:
            validate('confirm_bank_rollup',data['applied'],{'review_id':data['review_id']},context)
            if data['applied']['snapshot_digest']!=data['preview']['snapshot_digest'] or data['applied']['source_current'] is not data['source_current']:raise ValueError('State/result disagree.')
        return
    identifier(data['review_id'])
    if operation=='review_bank_rollup':
        if data.get('schema')!='sgacd-bank-rollup-review-v1' or data.get('period_reconciled') is not False:raise ValueError('First review cannot qualify a period.')
        b=data['preview'];preview(b,data,context)
        if b['period']!=payload['period'] or b['reconciliation_ids']!=sorted(payload['reconciliation_ids']) or b['revision']!=payload['expected_revision']+1:raise ValueError('Requested consolidation changed.')
        return
    if data.get('schema')!='sgacd-bank-rollup-result-v1' or data['review_id']!=payload['review_id'] or type(data.get('replayed')) is not bool or type(data.get('source_current')) is not bool or data.get('period_reconciled') is not data['source_current'] or data.get('requires_review') is not (not data['source_current']):raise ValueError('Consolidation qualification changed.')
    identifier(data['confirmation_id'])
    if not isinstance(data.get('snapshot_digest'),str) or not re.fullmatch('[0-9a-f]{64}',data['snapshot_digest']):raise ValueError('Missing consolidation fingerprint.')
    for k,limit in [('batch_count',20),('bank_row_count',200),('ledger_line_count',200)]:
        if type(data.get(k)) is not int or not 1<=data[k]<=limit:raise ValueError('Consolidation bounds changed.')

def preview(body,data,context):
    identifier(body['rollup_id']);snap=body['snapshot'];assessment=snap['assessment']
    if body['company_id']!=context['tenant_id'] or body['account_id']!=data['account_id'] or digest(snap)!=body['snapshot_digest'] or type(body['revision']) is not int or body['revision']<1 or snap.get('eligible') is not True or snap.get('allocations_complete') is not True or assessment['terms']!=body['period'] or assessment.get('source_independently_verified') is not False:raise ValueError('Reviewed snapshot changed.')
    if not isinstance(body['reconciliation_ids'],list) or len(set(body['reconciliation_ids']))!=len(body['reconciliation_ids']) or not 1<=len(body['reconciliation_ids'])<=20 or [p['reconciliation_id'] for p in snap['proofs']]!=body['reconciliation_ids']:raise ValueError('Different selected batches returned.')
    for row in snap['allocations']:
        if row['original_amount']!=row['allocated_amount']:raise ValueError('Partial cash line cannot qualify whole period.')
    if any(assessment[k]!='0.00' for k in ['opening_difference','closing_difference','flow_difference']) or assessment['unmatched_ledger_line_ids'] or assessment['unresolved_bank_rows']!=0 or assessment['eligible_for_period_reconciliation'] is not True:raise ValueError('Incomplete period cannot qualify.')
