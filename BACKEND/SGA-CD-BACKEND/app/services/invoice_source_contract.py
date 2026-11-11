"""Validate invoice-request responses; a queue receipt is never a fiscal receipt."""
from uuid import UUID

def uuid(value):
    if not isinstance(value,str) or str(UUID(value))!=value:raise ValueError('Canonical UUID required.')

def validate(operation,data,payload,selected):
    crm='crm' in operation;kind='crm_opportunity' if crm else 'reservation';key='opportunity_id' if crm else 'reservation_id'
    if not isinstance(data,dict) or data.get('schema')!='sgacd-commercial-request-result-v1' or data.get('company_id')!=selected['tenant_id'] or data.get('source_type')!=kind or data.get('source_id')!=payload[key]:raise ValueError('Invoice source mismatch.')
    for flag in ['ledger_written','fiscal_accepted','money_transferred','payment_verified','published']:
        if data.get(flag) is not False:raise ValueError('Unverified financial effect claimed.')
    uuid(data.get('review_id'))
    if type(data.get('revision')) is not int or not 1<=data['revision']<=2147483647:raise ValueError('Invalid source revision.')
    if operation.startswith('review_'):
        if data.get('status')!='REVIEWED' or data.get('request_created') is not False or data['revision']!=payload['expected_revision']+1:raise ValueError('Review is not request creation.')
    else:
        uuid(data.get('outbox_id'))
        if data.get('status')!='REQUEST_ONLY' or data.get('request_persisted') is not True or type(data.get('replayed')) is not bool or data.get('review_id')!=payload['review_id'] or data.get('outbox_status') not in {'PENDING','PROCESSED','ERROR'} or data.get('published_by_this_call') is not False or data.get('source_authority_verified') is not True or data.get('legal_tax_policy_verified') is not False:raise ValueError('Request persistence is not payment or fiscal acceptance.')
