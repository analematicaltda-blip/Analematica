"""Bounded, chronological scenario output; never financial execution authority."""
import re
import hashlib,json
from datetime import date,timedelta
from decimal import Decimal,localcontext,Context,ROUND_HALF_UP,InvalidOperation

def cents(value):
 if isinstance(value,bool) or not isinstance(value,(str,int,Decimal)) or isinstance(value,str) and len(value)>64:raise ValueError('Exact declared amount required.')
 with localcontext(Context(prec=64)):
  try:amount=Decimal(value)
  except InvalidOperation:raise ValueError('Invalid declared amount.') from None
  if not amount.is_finite() or abs(amount)>Decimal('999999999999.99') or amount!=amount.quantize(Decimal('.01')):raise ValueError('Declared amount outside exact cent range.')
  return int(amount*100)

def validate(data,payload,context):
 if not isinstance(data,dict) or set(data)!={'method','windows','summary','overlapping_holdouts','source','interpretation','production_qualified','financial_execution','ledger_written','tenant_id','currency'}:raise ValueError('Unexpected scenario output fields.')
 if data['method']!='chronological_multi_holdout_v1' or data['tenant_id']!=context['tenant_id'] or not isinstance(data['currency'],str) or not re.fullmatch('[A-Z]{3}',data['currency']) or data['source']!='operator_declared_windows_not_verified_bank_data':raise ValueError('Scenario context differs.')
 if any(data[k] is not False for k in ['production_qualified','financial_execution','ledger_written']):raise ValueError('Scenario cannot authorize financial action.')
 windows=data['windows'];requested=payload.get('windows')
 if not isinstance(requested,list) or not 2<=len(requested)<=4 or not isinstance(windows,list) or len(windows)!=len(requested) or type(data['overlapping_holdouts']) is not bool:raise ValueError('Bounded corresponding windows required.')
 money=lambda v:isinstance(v,str) and re.fullmatch(r'-?[0-9]{1,26}\.[0-9]{2}',v)
 previous=None;end=None;overlap=False
 for result,request in zip(windows,requested):
  if not isinstance(result,dict) or set(result)!={'method','forecast','holdout_start','holdout_end','holdout_count','outcome_digest','evaluations','mean_absolute_terminal_error_across_horizons','interpretation','production_qualified','financial_execution','ledger_written'}:raise ValueError('Unexpected window fields.')
  if result['method']!='single_chronological_holdout_v1' or any(result[k] is not False for k in ['production_qualified','financial_execution','ledger_written']):raise ValueError('Window authority invalid.')
  forecast=result['forecast'];scenario=request['scenario'];actuals=request['actuals']
  if not isinstance(forecast,dict) or forecast.get('source')!='operator_declared_scenario_not_ledger' or forecast.get('model_version')!='cash-bootstrap-v1' or any(forecast.get(k) is not False for k in ['production_qualified','financial_execution','ledger_written']):raise ValueError('Unsupported forecast.')
  if set(forecast)!={'model_version','runtime_python','source','input_digest','seed','paths','observation_start','observation_end','observation_count','forecast_end','opening_cash','results','assumptions','interval_interpretation','production_qualified','financial_execution','ledger_written'}:raise ValueError('Unexpected forecast fields.')
  if forecast.get('seed')!=scenario['seed'] or forecast.get('paths')!=scenario['paths'] or forecast.get('observation_start')!=scenario['observations'][0]['date'] or forecast.get('observation_end')!=scenario['observations'][-1]['date'] or forecast.get('observation_count')!=len(scenario['observations']):raise ValueError('Forecast sources differ.')
  origin=date.fromisoformat(forecast['observation_end']);start=date.fromisoformat(result['holdout_start']);last=date.fromisoformat(result['holdout_end'])
  if previous is not None and origin<=previous or start!=origin+timedelta(days=1) or last!=start+timedelta(days=364) or result['holdout_count']!=365 or len(actuals)!=365 or actuals[0]['date']!=start.isoformat() or actuals[-1]['date']!=last.isoformat():raise ValueError('Window dates differ.')
  if end is not None and start<=end:overlap=True
  previous=origin;end=last
  for field in ['input_digest']:
   if not isinstance(forecast.get(field),str) or not re.fullmatch('[0-9a-f]{64}',forecast[field]):raise ValueError('Forecast digest required.')
  if not isinstance(result['outcome_digest'],str) or not re.fullmatch('[0-9a-f]{64}',result['outcome_digest']) or not money(result['mean_absolute_terminal_error_across_horizons']):raise ValueError('Outcome proof required.')
  if not isinstance(forecast.get('results'),list) or len(forecast['results'])!=3 or not isinstance(result['evaluations'],list) or len(result['evaluations'])!=3:raise ValueError('Three horizons required.')
  # Reconcile held-out observations without rerunning the probabilistic model.
  # A self-consistent response can still refer to different submitted outcomes.
  if not money(forecast['opening_cash']) or cents(forecast['opening_cash'])!=cents(scenario['opening_cash']) or forecast['forecast_end']!=last.isoformat():raise ValueError('Forecast opening or end differs.')
  training=[{'date':row['date'],'net_cents':cents(row['net_cash_flow'])} for row in scenario['observations']]
  normalized={'opening_cents':cents(scenario['opening_cash']),'observations':training,'seed':scenario['seed'],'paths':scenario['paths'],'version':'cash-bootstrap-v1'}
  if hashlib.sha256(json.dumps(normalized,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=forecast['input_digest']:raise ValueError('Forecast input digest differs from request.')
  observed={};canonical=[];negative=False
  with localcontext(Context(prec=64)):
   cash=Decimal(cents(scenario['opening_cash']))/100
   for index,outcome in enumerate(actuals,1):
    if not isinstance(outcome,dict) or set(outcome)!={'date','net_cash_flow'} or outcome['date']!=(origin+timedelta(days=index)).isoformat():raise ValueError('Invalid held-out observation.')
    flow=Decimal(cents(outcome['net_cash_flow']))/100;cash+=flow;negative=negative or cash<0
    canonical.append({'date':outcome['date'],'net_cents':int(flow*100)})
    if index in [30,90,365]:observed[index]=(cash,negative)
  digest=hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  if digest!=result['outcome_digest']:raise ValueError('Outcome digest differs from request.')
  errors=[];previous_negative_count=0
  for days,row,evaluation in zip([30,90,365],forecast['results'],result['evaluations']):
   if not isinstance(row,dict) or not isinstance(evaluation,dict):raise ValueError('Horizon objects required.')
   if set(row)!={'days','end_date','ending_cash_p05','ending_cash_p50','ending_cash_p95','ending_cash_mean','paths_with_negative_cash','negative_cash_path_fraction'} or set(evaluation)!={'days','actual_ending_cash','predicted_ending_cash_p50','actual_minus_predicted','absolute_terminal_error','empirical_interval_contains_actual','realized_path_ever_negative','scenario_negative_cash_fraction'}:raise ValueError('Unexpected horizon fields.')
   if row.get('days')!=days or evaluation.get('days')!=days or row.get('end_date')!=(origin+timedelta(days=days)).isoformat() or not all(money(row.get(k)) for k in ['ending_cash_p05','ending_cash_p50','ending_cash_p95','ending_cash_mean']) or not all(money(evaluation.get(k)) for k in ['actual_ending_cash','predicted_ending_cash_p50','actual_minus_predicted','absolute_terminal_error']):raise ValueError('Forecast horizon or amounts invalid.')
   with localcontext(Context(prec=64)):
    low,median,high=[Decimal(row[k]) for k in ['ending_cash_p05','ending_cash_p50','ending_cash_p95']];actual=Decimal(evaluation['actual_ending_cash']);error=actual-median
    if actual!=observed[days][0] or evaluation['realized_path_ever_negative'] is not observed[days][1]:raise ValueError('Realized trajectory differs from submitted outcomes.')
    count=row['paths_with_negative_cash'];paths=forecast['paths']
    if type(paths) is not int or paths<1 or type(count) is not int or not previous_negative_count<=count<=paths:raise ValueError('Invalid negative-cash path count.')
    previous_negative_count=count
    fraction=format(Decimal(count)/paths,'.6f')
    if row['negative_cash_path_fraction']!=fraction or evaluation['scenario_negative_cash_fraction']!=fraction:raise ValueError('Negative-cash fraction differs from path count.')
    errors.append(abs(error))
    if not low<=median<=high or evaluation['predicted_ending_cash_p50']!=row['ending_cash_p50'] or Decimal(evaluation['actual_minus_predicted'])!=error or Decimal(evaluation['absolute_terminal_error'])!=abs(error) or evaluation['empirical_interval_contains_actual'] is not (low<=actual<=high):raise ValueError('Horizon evaluation does not reconcile.')
  with localcontext(Context(prec=64)):
   expected=format((sum(errors,Decimal(0))/3).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'.2f')
   if result['mean_absolute_terminal_error_across_horizons']!=expected:raise ValueError('Window error mean differs.')
 if data['overlapping_holdouts']!=overlap or not isinstance(data['summary'],list) or len(data['summary'])!=3:raise ValueError('Window aggregate differs.')
 for horizon,row in zip([30,90,365],data['summary']):
  if not isinstance(row,dict) or set(row)!={'days','windows','mean_absolute_terminal_error','interval_contains_actual_count','interval_contains_actual_fraction'}:raise ValueError('Unexpected summary fields.')
  if row.get('days')!=horizon or row.get('windows')!=len(windows) or not money(row.get('mean_absolute_terminal_error')) or type(row.get('interval_contains_actual_count')) is not int or not 0<=row['interval_contains_actual_count']<=len(windows):raise ValueError('Invalid descriptive summary.')
  with localcontext(Context(prec=64)):
   values=[w['evaluations'][[30,90,365].index(horizon)] for w in windows];mean=sum((Decimal(v['absolute_terminal_error']) for v in values),Decimal(0))/len(values);count=sum(int(v['empirical_interval_contains_actual']) for v in values)
   if row['mean_absolute_terminal_error']!=format(mean.quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'.2f') or row['interval_contains_actual_count']!=count or row['interval_contains_actual_fraction']!=format(Decimal(count)/len(values),'.6f'):raise ValueError('Window summary does not reconcile.')
 return data
