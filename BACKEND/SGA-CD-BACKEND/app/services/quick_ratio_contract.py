"""Exact read-only liquidity result: classification is declared, not certification."""
import re
from uuid import UUID
from decimal import Decimal,localcontext,Context,ROUND_HALF_UP
ROLES={'cash_equivalents','temporary_investments','immediate_receivables','current_liabilities'}
def money(value):
 if not isinstance(value,str) or not re.fullmatch(r'-?[0-9]{1,26}\.[0-9]{2}',value):raise ValueError('Exact balance required.')
 return Decimal(value)
def validate(data,*,company_id,cutoff):
 if not isinstance(data,dict) or data.get('tenant_id')!=company_id or data.get('cutoff_date')!=cutoff or data.get('unit')!='times' or data.get('source')!='primary_posted_ledger' or data.get('valuation')!='base_currency' or data.get('formula')!='(cash_equivalents+temporary_investments+immediate_receivables)/current_liabilities':raise ValueError('Ratio context mismatch.')
 if data.get('classification_scope')!='selected_accounts_reviewed_by_owner_not_independently_certified' or data.get('historical_policy') not in {'explicit_reviewed_revision_applied_to_cutoff','latest_reviewed_classification_applied_to_cutoff'} or data.get('reconstruction')!='current_posted_ledger_by_economic_date_not_original_publication_snapshot':raise ValueError('Unsupported classification authority.')
 if not isinstance(data.get('currency'),str) or not re.fullmatch('[A-Z]{3}',data['currency']) or any(data.get(k) is not True for k in ['read_only','posted_only']) or any(data.get(k) is not False for k in ['ledger_written','money_transferred']):raise ValueError('Invalid ratio status.')
 snapshot=data.get('snapshot')
 if not isinstance(snapshot,dict) or snapshot.get('database')!='primary' or snapshot.get('consistency')!='company_lock_shared_with_posting' or snapshot.get('historical_publication_snapshot') is not False:raise ValueError('Authoritative snapshot required.')
 allowed={'tenant_id','currency','cutoff_date','unit','formula','source','policy','value','classification_scope','historical_policy','reconstruction','read_only','posted_only','valuation','ledger_written','money_transferred','snapshot','unavailable_reason'}
 if data.get('policy') is not None:allowed|={'sources','totals'}
 if set(data)!=allowed:raise ValueError('Unexpected liquidity fields.')
 if set(snapshot)!={'database','consistency','ledger_tail_id','ledger_tail_hash','historical_publication_snapshot'}:raise ValueError('Unexpected snapshot fields.')
 tail=snapshot['ledger_tail_id'];digest=snapshot['ledger_tail_hash']
 if tail is None:
  if digest is not None:raise ValueError('Inconsistent empty ledger reference.')
 elif not isinstance(tail,str) or str(UUID(tail))!=tail or not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Invalid ledger reference.')
 if data.get('policy') is None:
  if data.get('value') is not None or data.get('unavailable_reason')!='REVIEWED_CLASSIFICATION_REQUIRED':raise ValueError('Unclassified ratio cannot claim a value.')
  return data
 policy=data['policy']
 if not isinstance(policy,dict) or set(policy)!={'id','revision','mapping','reviewer_id','evidence_digest','digest','created_at','verification'}:raise ValueError('Unexpected classification fields.')
 if policy.get('verification')!='reviewer_declared_not_independent_attestation':raise ValueError('Unsupported classification certification claim.')
 if type(policy.get('revision')) is not int or policy['revision']<1 or not isinstance(policy.get('mapping'),dict) or set(policy['mapping'])!=ROLES or set(data.get('sources',{}))!=ROLES or set(data.get('totals',{}))!=ROLES:raise ValueError('Explicit ratio sources required.')
 with localcontext(Context(prec=64)):
  totals={};negative=False;all_ids=set()
  for role in ROLES:
   rows=data['sources'][role];ids=set();total=Decimal(0)
   if not isinstance(rows,list) or len(rows)>1000:raise ValueError('Bounded source rows required.')
   for row in rows:
    if not isinstance(row,dict) or set(row)!={'account_id','balance'} or not isinstance(row['account_id'],str) or str(UUID(row['account_id']))!=row['account_id'] or row['account_id'] in all_ids:raise ValueError('Invalid/duplicate account provenance.')
    ids.add(row['account_id']);all_ids.add(row['account_id']);amount=money(row['balance']);negative=negative or amount<0;total+=amount
   if not isinstance(policy['mapping'][role],list) or len(policy['mapping'][role])!=len(ids) or set(policy['mapping'][role])!=ids or money(data['totals'][role])!=total:raise ValueError('Balances differ from reviewed classification.')
   totals[role]=total
  reason='NEGATIVE_ACCOUNT_BALANCE_REQUIRES_REVIEW' if negative else 'NON_POSITIVE_CURRENT_LIABILITIES' if totals['current_liabilities']<=0 else None
  if reason:
   if data.get('value') is not None or data.get('unavailable_reason')!=reason:raise ValueError('Noncalculable ratio claimed.')
  else:
   expected=(sum((totals[r] for r in ROLES if r!='current_liabilities'),Decimal(0))/totals['current_liabilities']).quantize(Decimal('.0001'),rounding=ROUND_HALF_UP)
   if data.get('value')!=format(expected,'.4f') or data.get('unavailable_reason') is not None:raise ValueError('Ratio does not reconcile with source balances.')
 return data
