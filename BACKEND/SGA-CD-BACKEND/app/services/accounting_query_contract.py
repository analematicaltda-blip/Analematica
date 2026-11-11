"""Verify read-only query sources and arithmetic, never generated SQL or actions."""
import re,unicodedata
from uuid import UUID
from decimal import Decimal,localcontext,Context,ROUND_HALF_EVEN
from datetime import date
from .quick_ratio_contract import validate as validate_ratio

QUESTIONS={
 'rentabilidad':'profitability','muestra la rentabilidad':'profitability','cual es el resultado neto de mi empresa':'profitability',
 'cual es la rentabilidad de mi empresa':'profitability','cual es mi rentabilidad':'profitability',
 'liquidez':'quick_ratio','liquidez acida':'quick_ratio','cual es mi liquidez acida':'quick_ratio','consulta mi liquidez acida':'quick_ratio',
 'estado de la cola de facturacion':'commercial_queue','estado de la cola comercial':'commercial_queue','como esta la cola de facturacion':'commercial_queue'}
def resolve(question):
 if not isinstance(question,str) or not 1<=len(question)<=240:raise ValueError('Bounded query required.')
 key=''.join(c for c in unicodedata.normalize('NFKD',question.casefold()) if not unicodedata.combining(c))
 key=' '.join(key.strip(' ¿?¡!.,\t\r\n').split())
 if key not in QUESTIONS:raise ValueError('Unsupported query.')
 return QUESTIONS[key]
def money(value):
 if not isinstance(value,str) or not re.fullmatch(r'-?[0-9]{1,26}\.[0-9]{2}',value):raise ValueError('Exact monetary amount required.')
 return Decimal(value)
def validate(data,payload,context):
 intent=resolve(payload.get('question'));fields={'schema','intent','company_id','read_only','execution','source','data','generated_sql','external_model_used','ledger_written','financial_action_authorized'}
 if not isinstance(data,dict) or set(data)!=fields or data['schema']!='sgacd-accounting-query-v1' or data['intent']!=intent or data['company_id']!=context['tenant_id'] or data['read_only'] is not True or data['execution']!='DETERMINISTIC_ALLOWLIST' or any(data[k] is not False for k in ['generated_sql','external_model_used','ledger_written','financial_action_authorized']):raise ValueError('Query authority/context differs.')
 body=data['data']
 if not isinstance(body,dict):raise ValueError('Structured source required.')
 if intent=='quick_ratio':
  if set(payload)!={'question','until'} or data['source']!='ratios.quick_ratio':raise ValueError('Ratio source differs.')
  validate_ratio(body,company_id=context['tenant_id'],cutoff=payload['until']);return
 if intent=='commercial_queue':
  fields={'company_id','read_only','transport_counts','fiscal_consumer_available','fiscal_receipt_verified','fiscal_acceptance','blocking_reason','outbox_status_is_fiscal_acceptance','financial_values_omitted','published_by_this_call','ledger_written'}
  if set(payload)!={'question'} or data['source']!='inspect_commercial_outbox' or set(body)!=fields or body['company_id']!=context['tenant_id'] or body['fiscal_acceptance']!='NOT_VERIFIED' or body['blocking_reason']!='FISCAL_CONSUMER_NOT_INTEGRATED' or body['read_only'] is not True or body['financial_values_omitted'] is not True or any(body[k] is not False for k in ['fiscal_consumer_available','fiscal_receipt_verified','outbox_status_is_fiscal_acceptance','published_by_this_call','ledger_written']):raise ValueError('Queue transport is not fiscal acceptance.')
  counts=body['transport_counts']
  if not isinstance(counts,dict) or set(counts)!={'invoice_requests','reservation_confirmations'}:raise ValueError('Queue sources differ.')
  for row in counts.values():
   if not isinstance(row,dict) or set(row)!={'PENDING','PROCESSED','ERROR','OTHER'} or any(type(v) is not int or not 0<=v<=9007199254740991 for v in row.values()):raise ValueError('Invalid queue counts.')
  return
 fields={'tenant_id','currency','start_date','end_date','posted_only','valuation','source','scope','revenue','expenses','net_profit','sources','net_margin','related_reports','pending_metrics','snapshot'}
 if set(payload)!={'question','since','until'} or data['source']!='ReportsEngine.get_profitability' or set(body)!=fields or body['tenant_id']!=context['tenant_id'] or body['start_date']!=payload['since'] or body['end_date']!=payload['until'] or body['posted_only'] is not True or body['valuation']!='base_currency' or body['source']!='primary_ledger' or body['scope']!='company' or not isinstance(body['currency'],str) or not re.fullmatch('[A-Z]{3}',body['currency']):raise ValueError('Profitability source differs.')
 start,end=date.fromisoformat(payload['since']),date.fromisoformat(payload['until'])
 if end<start or (end-start).days>366:raise ValueError('Bounded interval required.')
 snapshot=body['snapshot']
 if not isinstance(snapshot,dict) or set(snapshot)!={'database','consistency','ledger_tail_id','ledger_tail_hash','historical_publication_snapshot'} or snapshot['database']!='primary' or snapshot['consistency']!='company_lock_shared_with_posting' or snapshot['historical_publication_snapshot'] is not False:raise ValueError('Primary snapshot required.')
 tail,digest=snapshot['ledger_tail_id'],snapshot['ledger_tail_hash']
 if tail is None:
  if digest is not None:raise ValueError('Empty snapshot mismatch.')
 elif not isinstance(tail,str) or str(UUID(tail))!=tail or not isinstance(digest,str) or not re.fullmatch('[a-f0-9]{64}',digest):raise ValueError('Invalid snapshot proof.')
 if not isinstance(body['sources'],list) or len(body['sources'])>5000:raise ValueError('Bounded account provenance required.')
 with localcontext(Context(prec=64)):
  revenue=expenses=Decimal(0);seen=set()
  for row in body['sources']:
   if not isinstance(row,dict) or set(row)!={'account_id','code','type','net_amount'} or not isinstance(row['account_id'],str) or str(UUID(row['account_id']))!=row['account_id'] or row['account_id'] in seen or not isinstance(row['code'],str) or not 1<=len(row['code'])<=100:raise ValueError('Invalid account provenance.')
   seen.add(row['account_id']);amount=money(row['net_amount'])
   if row['type']=='REVENUE':revenue+=amount
   elif row['type'] in {'EXPENSE','COST_OF_SALES','PRODUCTION_COST'}:expenses+=amount
   else:raise ValueError('Unsupported account type.')
  if money(body['revenue'])!=revenue or money(body['expenses'])!=expenses or money(body['net_profit'])!=revenue-expenses:raise ValueError('Profitability does not reconcile to accounts.')
  margin=body['net_margin'];expected=format(((revenue-expenses)/revenue*100).quantize(Decimal('.0001'),rounding=ROUND_HALF_EVEN),'.4f') if revenue>0 else None
  if not isinstance(margin,dict) or set(margin)!={'value','unit','formula','unavailable_reason'} or margin['value']!=expected or margin['unit']!='percent' or margin['formula']!='(revenue-expenses)/revenue*100' or margin['unavailable_reason']!=(None if revenue>0 else 'NON_POSITIVE_REVENUE'):raise ValueError('Margin does not reconcile.')
 if body['related_reports']!={'quick_ratio':'liquidez-acida (requires reviewed classification)'} or body['pending_metrics']!={'revpar':'ROOM_REVENUE_MAPPING_AND_AVAILABLE_ROOM_NIGHTS_REQUIRED','goppar':'OPERATING_RESULT_MAPPING_AND_AVAILABLE_ROOM_NIGHTS_REQUIRED','package_margin':'VERIFIED_PACKAGE_COST_AND_REVENUE_ATTRIBUTION_REQUIRED'}:raise ValueError('Unsupported operational metric claim.')
