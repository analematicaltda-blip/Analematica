"""Opt-in read-only provider costs. Planning budgets and estimates are not costs."""
import os,json,re,time
from urllib.parse import urlsplit
from decimal import Decimal,localcontext,Context,InvalidOperation
import httpx
from .contract import SYSTEM
from .crm import CRMError
from .analytics_forecast import money

def collect(crm,since,until,client_factory=None):
 from datetime import date
 try:
  if date.fromisoformat(since).isoformat()!=since or date.fromisoformat(until).isoformat()!=until or since>until:raise ValueError()
 except (ValueError,TypeError):raise CRMError('ANALYTICS_DATE_RANGE') from None
 if os.environ.get('COMMERCIAL_ANALYTICS_PROVIDER_READ_ENABLED')!='1':raise CRMError('ANALYTICS_PROVIDER_READ_DISABLED',503)
 key=SYSTEM+':'+crm.store.scope+':'+(getattr(crm.store,'provider',None) or '-')
 try:profiles=json.loads(os.environ.get('COMMERCIAL_ANALYTICS_ACCOUNTS','{}'))[key]
 except (KeyError,ValueError,TypeError):raise CRMError('ANALYTICS_PROVIDER_PROFILE_REQUIRED',503) from None
 if not isinstance(profiles,dict) or not profiles or len(profiles)>20:raise CRMError('ANALYTICS_PROVIDER_PROFILE_REQUIRED',503)
 rows=[];proofs=[];calls=0;started=time.monotonic();accounts_seen=set()
 with (client_factory or httpx.Client)(timeout=httpx.Timeout(15,connect=3),follow_redirects=False,trust_env=False) as client:
  def request(method,url,headers,**kw):
   nonlocal calls
   calls+=1
   if calls>50 or time.monotonic()-started>120:raise ValueError()
   crm.authorize()
   with client.stream(method,url,headers=headers,**kw) as response:
    if response.status_code!=200:raise ValueError()
    raw=b''
    for chunk in response.iter_bytes():
     raw+=chunk
     if len(raw)>262144:raise ValueError()
    obj=json.loads(raw)
    if not isinstance(obj,dict):raise ValueError()
    return obj
  def record(platform,account,campaign,day,amount,impressions,clicks):
   from datetime import date
   if not isinstance(campaign,str) or not re.fullmatch('[A-Za-z0-9_-]{1,100}',campaign) or not isinstance(day,str) or date.fromisoformat(day).isoformat()!=day or not since<=day<=until:raise ValueError()
   for n in (impressions,clicks):
    if not isinstance(n,str) or not re.fullmatch('[0-9]{1,15}',n):raise ValueError()
   if int(clicks)>int(impressions):raise ValueError()
   if not isinstance(amount,str) or len(amount)>40:raise ValueError()
   with localcontext(Context(prec=50)):
    exact=Decimal(amount)
    if not exact.is_finite() or abs(exact)>Decimal('1000000000000') or exact!=exact.quantize(Decimal('.000001')):raise ValueError()
   rows.append({'platform':platform,'account':account,'campaign':campaign,'date':day,'cost_cop':format(exact,'f'),'impressions':int(impressions),'clicks':int(clicks)})
   if len(rows)>500:raise ValueError()
  try:
   for alias,p in profiles.items():
    if not isinstance(p,dict) or set(p)!={'platform','account_id','owner_id','credential_env','developer_token_env','api_version'} or p['owner_id']!=crm.actor or not re.fullmatch('[A-Za-z0-9_-]{1,80}',alias):raise ValueError()
    if not re.fullmatch('COMMERCIAL_ANALYTICS_SECRET_[A-Z0-9_]{1,60}',p['credential_env']):raise ValueError()
    token=os.environ.get(p['credential_env'],'')
    if not 16<=len(token)<=4096 or any(ord(c)<33 or ord(c)>126 for c in token):raise ValueError()
    account=p['account_id'];platform=p['platform']
    if not isinstance(account,str) or not re.fullmatch('[0-9]{1,30}',account):raise ValueError()
    account_key=(platform,account)
    if account_key in accounts_seen:raise ValueError()
    accounts_seen.add(account_key)
    if platform=='META':
     headers={'Authorization':'Bearer '+token};base='https://graph.facebook.com/v22.0/';identity=request('GET',base+'act_'+account,headers,params={'fields':'id,account_id,currency'})
     if identity.get('account_id')!=account or identity.get('id')!='act_'+account or identity.get('currency')!='COP':raise ValueError()
     cursor=None;seen=set()
     for page in range(6):
      if page==5:raise ValueError()
      params={'fields':'account_id,campaign_id,date_start,date_stop,spend,impressions,clicks','level':'campaign','time_increment':1,'time_range':json.dumps({'since':since,'until':until}),'limit':100}
      if cursor:params['after']=cursor
      data=request('GET',base+'act_'+account+'/insights',headers,params=params)
      if not isinstance(data.get('data'),list):raise ValueError()
      for row in data['data']:
       if row.get('account_id')!=account or row.get('date_start')!=row.get('date_stop'):raise ValueError()
       record(platform,alias,row['campaign_id'],row['date_start'],row['spend'],row['impressions'],row['clicks'])
      paging=data.get('paging',{})
      if not paging.get('next'):break
      cursor=paging.get('cursors',{}).get('after')
      if not isinstance(cursor,str) or not 1<=len(cursor)<=2000 or cursor in seen:raise ValueError()
      seen.add(cursor)
    elif platform=='TIKTOK':
     headers={'Access-Token':token};base='https://business-api.tiktok.com/open_api/v1.3/'
     def tk(path,params):
      obj=request('GET',base+path,headers,params=params)
      if obj.get('code')!=0 or not isinstance(obj.get('data'),dict):raise ValueError()
      return obj['data']
     identity=tk('advertiser/info/',{'advertiser_ids':json.dumps([account]),'fields':json.dumps(['advertiser_id','currency'])})
     if not any(str(v.get('advertiser_id'))==account and v.get('currency')=='COP' for v in identity.get('list',[])):raise ValueError()
     first_row=len(rows);expected_count=None;expected_pages=None
     for page in range(1,6):
      data=tk('report/integrated/get/',{'advertiser_id':account,'service_type':'AUCTION','report_type':'BASIC','data_level':'AUCTION_CAMPAIGN','dimensions':json.dumps(['campaign_id','stat_time_day']),'metrics':json.dumps(['spend','impressions','clicks']),'start_date':since,'end_date':until,'page':page,'page_size':100});items=data.get('list');info=data.get('page_info',{})
      if not isinstance(items,list) or type(info.get('total_page'))!=int or not 0<=info['total_page']<=5 or type(info.get('total_number'))!=int or not 0<=info['total_number']<=500:raise ValueError()
      if expected_count is None:expected_count=info['total_number'];expected_pages=info['total_page']
      if info['total_number']!=expected_count or info['total_page']!=expected_pages or expected_pages==0 and (expected_count!=0 or items):raise ValueError()
      for row in items:
       m=row['metrics'];d=row['dimensions'];record(platform,alias,d['campaign_id'],d['stat_time_day'][:10],m['spend'],m['impressions'],m['clicks'])
      if page>=info['total_page']:break
     if len(rows)-first_row!=expected_count:raise ValueError()
    elif platform=='GOOGLE_YOUTUBE':
     if not re.fullmatch('v[0-9]{1,3}',p['api_version']) or not re.fullmatch('COMMERCIAL_ANALYTICS_SECRET_[A-Z0-9_]{1,60}',p['developer_token_env']):raise ValueError()
     developer=os.environ.get(p['developer_token_env'],'')
     if not 16<=len(developer)<=4096 or any(ord(c)<33 or ord(c)>126 for c in developer):raise ValueError()
     headers={'Authorization':'Bearer '+token,'developer-token':developer};url='https://googleads.googleapis.com/'+p['api_version']+'/customers/'+account+'/googleAds:search'
     identity=request('POST',url,headers,json={'query':'SELECT customer.id, customer.currency_code FROM customer LIMIT 1'})
     if not any(str(row.get('customer',{}).get('id'))==account and row['customer'].get('currencyCode')=='COP' for row in identity.get('results',[])):raise ValueError()
     query="SELECT campaign.id, segments.date, metrics.cost_micros, metrics.impressions, metrics.clicks FROM campaign WHERE segments.date BETWEEN '"+since+"' AND '"+until+"'";cursor=None;seen=set()
     for page in range(6):
      if page==5:raise ValueError()
      payload={'query':query}
      if cursor:payload['pageToken']=cursor
      data=request('POST',url,headers,json=payload)
      if not isinstance(data.get('results',[]),list) or 'results' not in data and not isinstance(data.get('fieldMask'),str):raise ValueError()
      for row in data.get('results',[]):
       metrics=row['metrics'];micro=metrics['costMicros']
       if not isinstance(micro,str) or not re.fullmatch('[0-9]{1,18}',micro):raise ValueError()
       with localcontext(Context(prec=50)):amount=Decimal(micro)/1000000
       # Preserve reported micros exactly; rounding is only a labelled display step.
       record(platform,alias,str(row['campaign']['id']),row['segments']['date'],format(amount,'f'),metrics['impressions'],metrics['clicks'])
      cursor=data.get('nextPageToken')
      if not cursor:break
      if not isinstance(cursor,str) or len(cursor)>2000 or cursor in seen:raise ValueError()
      seen.add(cursor)
    else:raise ValueError()
    proofs.append({'account':alias,'platform':platform,'currency':'COP','scope':'CONFIGURED_ACCOUNT_ONLY','api_response_received':True,'real_provider_qualified':False})
   keys=[(r['platform'],r['account'],r['campaign'],r['date']) for r in rows]
   if len(keys)!=len(set(keys)):raise ValueError()
   return {'rows':rows,'accounts':proofs,'coverage':'CONFIGURED_ACCOUNTS_ONLY','real_provider_qualified':False}
  except (httpx.HTTPError,ValueError,TypeError,KeyError,AttributeError,InvalidOperation):raise CRMError('ANALYTICS_PROVIDER_REVIEW_REQUIRED',503) from None
