"""Deterministic temporal baseline. No synthesized gaps, model or causal claim."""
from datetime import date,timedelta
from decimal import Decimal,localcontext,InvalidOperation,Context
from .crm import CRMError
def money(value):
 if not isinstance(value,str) or len(value)>40:raise CRMError('ANALYTICS_EXACT_MONEY_REQUIRED')
 try:
  d=Decimal(value)
  if not d.is_finite() or d.copy_abs()>Decimal('100000000000000000000') or d!=d.quantize(Decimal('.01')):raise ValueError()
  return d
 except (InvalidOperation,ValueError):raise CRMError('ANALYTICS_EXACT_MONEY_REQUIRED') from None
def forecast(series,horizon=7):
 if type(horizon)!=int or not 1<=horizon<=30 or not isinstance(series,list) or len(series)>366:raise CRMError('ANALYTICS_FORECAST_LIMIT')
 values=[];previous=None
 for row in series:
  if not isinstance(row,dict) or set(row)!={'date','value'}:raise CRMError('ANALYTICS_DAILY_SERIES_REQUIRED')
  try:day=date.fromisoformat(row['date'])
  except (ValueError,TypeError):raise CRMError('ANALYTICS_DAILY_SERIES_REQUIRED') from None
  if day.isoformat()!=row['date'] or previous is not None and day!=previous+timedelta(days=1):raise CRMError('ANALYTICS_EXPLICIT_CONTIGUOUS_DAYS_REQUIRED')
  previous=day;values.append(money(row['value']))
 if len(values)<35 or not any(values):return {'state':'INSUFFICIENT_REVIEWED_HISTORY','predictions':[],'calibrated_for_production':False,'required_daily_points':35}
 with localcontext(Context(prec=50)):
  def estimate(history,model):return history[-1] if model=='LAST_VALUE' else sum(history[-7:])/7
  candidates=('LAST_VALUE','MEAN_7');split=len(values)-14
  validation={model:sum(abs(values[i]-estimate(values[:i],model)) for i in range(split,split+7))/7 for model in candidates};selected=min(candidates,key=lambda k:(validation[k],k));test_errors=[abs(values[i]-estimate(values[:i],selected)) for i in range(split+7,len(values))];mae=sum(test_errors)/7;history=list(values);pred=[]
  for n in range(1,horizon+1):
   point=estimate(history,selected);history.append(point);pred.append({'date':(previous+timedelta(days=n)).isoformat(),'value':format(point.quantize(Decimal('.01')),'.2f')})
  return {'state':'BASELINE_ESTIMATE','model':selected,'predictions':pred,'validation_mae':{k:format(v.quantize(Decimal('.01')),'.2f') for k,v in validation.items()},'test_mae':format(mae.quantize(Decimal('.01')),'.2f'),'training_points':split,'validation_points':7,'test_points':7,'selection_until':series[split+6]['date'],'test_from':series[split+7]['date'],'calibrated_for_production':False,'assumptions':['Explicit consecutive economic days; zeros must come from a complete declared source','Past-only walk-forward validation then independent seven-day test','No seasonality, interventions, confidence probability or guaranteed future return']}
