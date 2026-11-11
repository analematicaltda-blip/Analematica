"""Recoverable rehearsal is never a payment token or an executable desktop job."""
import json,hashlib,re
from uuid import UUID
from datetime import datetime
FLAGS={'payment_executed','bank_destination_verified','source_independently_verified','network_called','desktop_job_created','ledger_written','usable_as_payment_authorization'}
def validate_state(data,payload,context):
 fields={'schema','company_id','request_id','plan_digest','status','replayed','intent','expires_at','read_only','confirmations_restored','recorded_confirmations','next_step','can_simulate','can_cancel'}|FLAGS
 if not isinstance(data,dict) or set(data)!=fields or data['schema']!='sgacd-financial-rehearsal-result-v1' or data['company_id']!=context['tenant_id'] or data['request_id']!=payload['request_id'] or data['read_only'] is not True or data['confirmations_restored'] is not False or data['replayed'] is not False or any(data[k] is not False for k in FLAGS):raise ValueError('Rehearsal authority differs.')
 intent=data['intent']
 if not isinstance(intent,dict) or set(intent)!={'schema','company_id','request_id','purpose','amount','currency','beneficiary_ref','source_evidence_digest'} or intent['schema']!='sgacd-financial-rehearsal-v1' or intent['company_id']!=context['tenant_id'] or intent['request_id']!=data['request_id'] or intent['purpose'] not in ['SUPPLIER_PAYMENT','PAYROLL_BATCH'] or intent['currency']!='COP':raise ValueError('Bound intent required.')
 for key in ['company_id','request_id','beneficiary_ref']:
  if not isinstance(intent[key],str) or str(UUID(intent[key]))!=intent[key]:raise ValueError('Canonical scoped identifier required.')
 if not isinstance(intent['amount'],str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,11})\.[0-9]{2}',intent['amount']) or int(intent['amount'].replace('.',''))<=0 or not isinstance(intent['source_evidence_digest'],str) or not re.fullmatch('[a-f0-9]{64}',intent['source_evidence_digest']):raise ValueError('Exact reviewed intent required.')
 digest=hashlib.sha256(json.dumps(intent,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
 if digest!=data['plan_digest'] or not isinstance(data['expires_at'],str) or datetime.fromisoformat(data['expires_at']).tzinfo is None:raise ValueError('Digest or expiry invalid.')
 status=data['status'];count=data['recorded_confirmations']
 if type(count) is not int or not 0<=count<=2 or status not in ['PREPARED','CONFIRMED_1','CONFIRMED_2','SIMULATED_ONLY','EXPIRED','CANCELLED']:raise ValueError('Invalid rehearsal state.')
 expected={'PREPARED':0,'CONFIRMED_1':1,'CONFIRMED_2':2,'SIMULATED_ONLY':2}
 if status in expected and count!=expected[status] or data['next_step']!=(1 if status=='PREPARED' else 2 if status=='CONFIRMED_1' else None) or type(data['next_step']) is bool or data['can_simulate'] is not (status=='CONFIRMED_2') or data['can_cancel'] is not (status!='CANCELLED'):raise ValueError('Inconsistent confirmation recovery.')
