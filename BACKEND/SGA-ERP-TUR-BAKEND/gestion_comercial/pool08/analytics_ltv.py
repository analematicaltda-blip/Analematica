"""Finite-horizon LTV scenario from verified revenue and explicitly reviewed assumptions.
This is a declared gross-margin scenario, not a claim of measured lifetime profit.
"""
import json,os,re
from decimal import Decimal,Context,localcontext,InvalidOperation
from datetime import date
from .crm import CRMError,digest,moment
from .contract import SYSTEM

def estimate(crm,economics,since,until,now):
 empty={'value':None,'state':'REVIEWED_LIFETIME_MARGIN_AND_RETENTION_REQUIRED','observed_ARPU_is_LTV':False,'calibrated_for_production':False}
 if economics is None:return {**empty,'state':'LEDGER_SOURCE_UNAVAILABLE'}
 key=SYSTEM+':'+crm.store.scope+':'+(getattr(crm.store,'provider',None) or '-')
 try:profile=json.loads(os.environ.get('COMMERCIAL_ANALYTICS_LTV_POLICIES','{}')).get(key)
 except (ValueError,AttributeError):raise CRMError('ANALYTICS_LTV_POLICY_REVIEW_REQUIRED',503) from None
 if profile is None:return empty
 fields={'version','owner_ref','reviewer_ref','support_digest','valid_from','valid_until','gross_margin_fraction','monthly_churn_fraction','horizon_months','justification'}
 try:
  if not isinstance(profile,dict) or set(profile)!=fields or profile['owner_ref']!=crm.actor or not isinstance(profile['version'],str) or not re.fullmatch('[A-Za-z0-9_.-]{1,80}',profile['version']) or not isinstance(profile['reviewer_ref'],str) or not 1<=len(profile['reviewer_ref'])<=96 or not re.fullmatch('[a-f0-9]{64}',profile['support_digest']) or not isinstance(profile['justification'],str) or not 10<=len(profile['justification'])<=500:raise ValueError()
  if not moment(profile['valid_from'])<=now<moment(profile['valid_until']) or moment(profile['valid_until'])<=moment(profile['valid_from']):raise ValueError()
  days=(date.fromisoformat(until)-date.fromisoformat(since)).days+1;months=profile['horizon_months']
  if type(months)!=int or not 1<=months<=120:raise ValueError()
  for field in ('gross_margin_fraction','monthly_churn_fraction'):
   if not isinstance(profile[field],str) or not re.fullmatch(r'[01](?:\.[0-9]{1,6})?',profile[field]):raise ValueError()
  margin=Decimal(profile['gross_margin_fraction']);churn=Decimal(profile['monthly_churn_fraction'])
  if not 0<=margin<=1 or not 0<churn<=1:raise ValueError()
 except (ValueError,TypeError,InvalidOperation,CRMError):raise CRMError('ANALYTICS_LTV_POLICY_REVIEW_REQUIRED',503) from None
 rows=[r for r in economics['rows'] if since<=r['date']<=until];customers={r['contact_id'] for r in rows if r['kind']=='SALE'}
 if days<30 or not customers:return {**empty,'state':'INSUFFICIENT_OBSERVED_COHORT','policy_digest':digest(profile),'required_observed_days':30}
 with localcontext(Context(prec=50)):
  revenue=sum((Decimal(r['amount']) for r in rows),Decimal('0'))
  if revenue<0:return {**empty,'state':'NEGATIVE_NET_REVENUE_REVIEW_REQUIRED','policy_digest':digest(profile)}
  monthly=revenue*30/Decimal(days)/len(customers);value=monthly*margin*(1-(1-churn)**months)/churn
  return {'value':format(value.quantize(Decimal('.01')),'.2f'),'currency':'COP','state':'DECLARED_ASSUMPTION_SCENARIO','metric':'FINITE_HORIZON_EXPECTED_GROSS_MARGIN_PER_OBSERVED_MODULE_CUSTOMER','monthly_observed_revenue_per_customer_cop':format(monthly.quantize(Decimal('.01')),'.2f'),'gross_margin_fraction':profile['gross_margin_fraction'],'monthly_churn_fraction':profile['monthly_churn_fraction'],'horizon_months':months,'observed_days':days,'observed_customers':len(customers),'policy_version':profile['version'],'policy_digest':digest(profile),'support_digest':profile['support_digest'],'scope':economics['scope'],'observed_ARPU_is_LTV':False,'calibrated_for_production':False,'support_authenticity_verified':False,'assumptions':['Revenue and reversals come from verified module journals, not all company revenue','Monthly ARPU uses a declared 30-day normalization and the observed cohort','Constant declared margin and monthly churn; finite horizon, no discounting or causal guarantee','Includes no unmeasured acquisition cost or operating overhead; not net lifetime profit']}
