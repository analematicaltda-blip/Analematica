"""Validate recovery responses crossing the authenticated corporate boundary."""
from uuid import UUID
import hashlib,json


def validate(operation,data,payload,context):
    if data.get('company_id')!=context['tenant_id']:raise ValueError('Foreign recovery response.')
    if operation=='esg_report':
        if data.get('schema')!='sgacd-esg-draft-v1' or data.get('since')!=payload['since'] or data.get('until')!=payload['until'] or data.get('read_only') is not True or any(data.get(k) is not False for k in ['esg_certified','supports_independently_verified','applicability_independently_verified','ledger_written','money_transferred']):raise ValueError('ESG cannot imply certification.')
        body={k:v for k,v in data.items() if k!='report_digest'}
        digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
        if data.get('report_digest')!=digest or [{k:m[k] for k in ('framework','version','disclosure','boundary','applicability_reason','evidence_digest')} for m in data['disclosures']]!=payload['mappings']:raise ValueError('ESG mapping/report changed.')
    elif operation in {'bank_group_state','review_bank_group_release','confirm_bank_group_release'}:
        if data.get('ledger_written') is not False or data.get('bank_verified') is not False:raise ValueError('Group recovery is not financial settlement.')
        if operation=='bank_group_state' and (data.get('read_only') is not True or data.get('confirmations_restored') is not False):raise ValueError('Recovery cannot authorize.')
        if operation=='confirm_bank_group_release' and (data.get('released') is not True or data.get('fully_reconciled') is not False):raise ValueError('Released reconciliation is not active.')
    elif operation=='purchase_history':
        if data.get('invoice_id')!=payload['invoice_id'] or data.get('read_only') is not True or data.get('confirmations_restored') is not False:raise ValueError('Invalid purchase history.')
    elif operation in {'review_bank_groups','confirm_bank_groups'}:
        if data.get('ledger_written') is not False or data.get('bank_verified') is not False:raise ValueError('Grouped reconciliation cannot post funds.')
        if operation=='review_bank_groups':UUID(data['review_id'])
        else:
            UUID(data['reconciliation_id'])
            if data.get('review_id')!=payload['review_id'] or data.get('money_transferred') is not False or data.get('fully_reconciled') is not (data.get('associations_confirmed') is True and data['coverage']['unresolved_rows']==0 and not data.get('ledger_remainders')):raise ValueError('Partial group cannot claim completeness.')
    else:
        UUID(data['review_id'] if operation.startswith('review_') else data['correction_id'] if operation=='confirm_purchase_correction' else data['journal_id'])
        if data.get('ledger_written') is not (operation=='confirm_purchase_return'):raise ValueError('Unexpected recovery write.')
        if operation=='confirm_purchase_return' and data.get('money_transferred') is not False:raise ValueError('A purchase return is not a payment.')
