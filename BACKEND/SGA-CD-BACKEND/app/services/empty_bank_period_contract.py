"""Strict shared-ledger response contract for declared zero-activity periods."""
from uuid import UUID

def validate(operation,data,payload,context):
    if data.get('schema')!='sgacd-empty-bank-period-v1' or data.get('company_id')!=context['tenant_id']:raise ValueError('Foreign period response.')
    for key in ['request_id','account_id','review_id']:UUID(data[key])
    for key in ['source_current','historically_confirmed','period_reconciled','requires_review']:
        if type(data.get(key)) is not bool:raise ValueError('Explicit boolean required.')
    if any(data.get(k) is not False for k in ['confirmations_restored','bank_verified','ledger_written','money_transferred']) or data.get('read_only') is not True:raise ValueError('Period metadata is not a bank payment.')
    if data['period_reconciled']!=(data['source_current'] and data['historically_confirmed']) or data['requires_review']==data['source_current']:raise ValueError('Invalid qualification.')
    assessment=data.get('assessment',{})
    if assessment.get('schema')!='sgacd-bank-period-assessment-v1' or assessment.get('currency')!='COP' or assessment.get('source_independently_verified') is not False or assessment.get('eligible_for_period_reconciliation') is not True:raise ValueError('Explicit declared-period evidence required.')
    if any(assessment.get(k)!='0.00' for k in ['bank_in','bank_out','ledger_in','ledger_out','opening_difference','closing_difference','flow_difference']) or assessment.get('ledger_period_rows')!=0 or assessment.get('unmatched_ledger_line_ids')!=[] or assessment.get('unresolved_bank_rows')!=0:raise ValueError('A zero-activity report cannot conceal movements.')
    if operation=='review_empty_bank_period':
        if data['account_id']!=payload['account_id'] or data['request_id']!=payload['request_id'] or assessment.get('terms')!=payload['period']:raise ValueError('Reviewed period differs from request.')
    elif data['review_id']!=payload['review_id']:raise ValueError('Different review returned.')
    if operation=='confirm_empty_bank_period' and data['historically_confirmed'] is not True:raise ValueError('Missing second-confirmation evidence.')
