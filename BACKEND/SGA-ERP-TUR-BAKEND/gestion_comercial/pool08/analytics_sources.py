"""Bounded current records and verified module-ledger economics; no mutation."""
from datetime import datetime,timezone,date
from decimal import Decimal,localcontext,Context
from collections import Counter,defaultdict
from .crm import CRMError,moment
from .contract import SYSTEM
from .analytics_forecast import money
LIMIT=500

def chain(store,item):
 from .analytics import digest
 events=list(store.events(item['id']));previous='0'*64
 for event in events:
  if event.get('previous_event_digest')!=previous or event.get('event_digest')!=digest({k:v for k,v in event.items() if k!='event_digest'}):raise CRMError('ANALYTICS_SOURCE_HISTORY_INVALID',503)
  previous=event['event_digest']
 if not events or previous!=item.get('last_event_digest') or len(events)!=item['revision'] or events[-1]['result_digest']!=digest({k:v for k,v in item.items() if k!='last_event_digest'}):raise CRMError('ANALYTICS_SOURCE_INTEGRITY_INVALID',503)

def documents(store):
 result=[];offset=0
 while True:
  rows,more=store.list('','',offset,50)
  for row in rows:chain(store,row);result.append(row)
  if len(result)>LIMIT or more and len(result)>=LIMIT:raise CRMError('ANALYTICS_SOURCE_LIMIT',503)
  if not more:return result
  offset+=50

def contacts(crm):
 result=[];offset=0
 while True:
  data=crm.list(offset=offset,limit=50)
  for row in data['contacts']:result.append(crm.get(row['id']))
  if len(result)>LIMIT or data['next_offset'] is not None and len(result)>=LIMIT:raise CRMError('ANALYTICS_SOURCE_LIMIT',503)
  if data['next_offset'] is None:return result
  offset=data['next_offset']

def opportunities(crm):
 from .opportunities import Opportunities
 from .opportunity_store import Store
 service=Opportunities(Store(crm.store),crm);result=[];offset=0
 while True:
  data=service.list(offset=offset,limit=50);result.extend(data['opportunities'])
  if len(result)>LIMIT or data['next_offset'] is not None and len(result)>=LIMIT:raise CRMError('ANALYTICS_SOURCE_LIMIT',503)
  if data['next_offset'] is None:return result
  offset=data['next_offset']

def income(crm,sales,remote_reader=None):
 if any(d.get('pending') or str(d['status']).startswith('PENDING') for d in sales):raise CRMError('ANALYTICS_SALE_OUTCOME_UNCERTAIN',503)
 live=[d for d in sales if d['status'] in ('CONFIRMED','REVERSAL_REVIEWED','REVERSED')]
 if SYSTEM=='sga-cd' and live:
  if remote_reader is None:raise CRMError('ANALYTICS_REMOTE_LEDGER_NOT_REVALIDATED',503)
  rows=[];proof=[]
  for d in live:
   crm.authorize();remote=remote_reader(d)
   if not isinstance(remote,dict) or remote.get('scope')!='VERIFIED_COMMERCIAL_MODULE_JOURNALS_ONLY':raise CRMError('ANALYTICS_REMOTE_LEDGER_NOT_REVALIDATED',503)
   for row in remote['rows']:
    rows.append({**row,'sale_id':d['id'],'contact_id':d['source']['content']['contact_id']})
   proof.extend(remote['proof'])
  return {'rows':rows,'proof':proof,'scope':'VERIFIED_COMMERCIAL_MODULE_JOURNALS_ONLY','not_all_company_revenue':True,'posted_module_sales':len(live)}
 rows=[];proof=[]
 for d in live:
  from .sales_ledger import Ledger
  from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
  from apps.core_erp.accounting.ledger_engine import LedgerEngine
  if d.get('ledger_written') is not True or not d.get('journal'):raise CRMError('ANALYTICS_POSTED_JOURNAL_REQUIRED',503)
  original=Ledger(crm).verify(d);recognized=d['review']['preview']['revenue_recognized'];contra=d['review']['terms']['accounts']['contra'];entries=[('SALE',original)]
  if d['status']=='REVERSED':
   rev=d.get('reversal') or {};reversal=JournalEntry.plain_objects.filter(pk=rev.get('id'),tenant_id=crm.store.scope,is_posted=True,reversed_entry_id=original.pk).first()
   if reversal is None or reversal.system_hash!=rev.get('hash') or LedgerEngine.calculate_hash(reversal)!=reversal.system_hash:raise CRMError('ANALYTICS_REVERSAL_INTEGRITY_REQUIRED',503)
   entries.append(('REVERSAL',reversal))
  for kind,entry in entries:
   proof.append({'journal':str(entry.pk),'hash':entry.system_hash})
   if not recognized:continue
   lines=list(LedgerEntry.plain_objects.filter(journal_entry_id=entry.pk,account_id=contra,tenant_id=crm.store.scope).select_related('account'))
   if not lines or any(line.account.type!='REVENUE' for line in lines):raise CRMError('ANALYTICS_REVENUE_CLASSIFICATION_REQUIRED',503)
   with localcontext(Context(prec=50)):amount=sum((line.credit_amount-line.debit_amount for line in lines),Decimal('0'))
   rows.append({'sale_id':d['id'],'contact_id':d['source']['content']['contact_id'],'date':entry.date.isoformat(),'amount':format(amount,'.2f'),'kind':kind,'journal_hash':entry.system_hash})
 return {'rows':rows,'proof':proof,'scope':'VERIFIED_COMMERCIAL_MODULE_JOURNALS_ONLY','not_all_company_revenue':True,'posted_module_sales':len(live)}

def attribution(crm,rows,economics=None,since=None,until=None):
 from .capture_store import Store
 store=Store(crm.store);groups={};members={};missing=0;withdrawn=0
 for c in rows:
  origin=c.get('landing_attribution');consent=c.get('consents',{}).get('EMAIL:MARKETING',{})
  if c['status']=='WITHDRAWN':withdrawn+=1;continue
  if not origin or consent.get('granted') is not True or not consent.get('expires_at') or moment(consent['expires_at'])<=datetime.now(timezone.utc):missing+=1;continue
  capture=store.get(origin.get('capture_id'))
  if not capture:raise CRMError('ANALYTICS_CAPTURE_SOURCE_MISSING',503)
  chain(store,capture)
  if capture.get('withdrawn_at') or capture.get('contact_id')!=c['id'] or capture.get('source')!=origin:raise CRMError('ANALYTICS_ATTRIBUTION_REVIEW_REQUIRED',503)
  utm=origin.get('utm',{});key=(origin['page_id'],utm.get('utm_source',''),utm.get('utm_campaign',''))
  if key not in groups:groups[key]={'page_id':key[0],'declared_channel':key[1],'declared_campaign':key[2],'contacts':0,'crm_customers':0,'method':'CONSENTED_CAPTURE_DECLARATION','provider_attribution_verified':False}
  groups[key]['contacts']+=1;groups[key]['crm_customers']+=int(c['status']=='CUSTOMER');members[c['id']]=key
 for key,group in groups.items():
  linked=[] if economics is None else [r for r in economics['rows'] if members.get(r['contact_id'])==key and since<=r['date']<=until]
  with localcontext(Context(prec=50)):net=sum((money(r['amount']) for r in linked),Decimal('0'))
  group['period_recognized_sales']=None if economics is None else sum(r['kind']=='SALE' for r in linked)
  group['period_recognized_reversals']=None if economics is None else sum(r['kind']=='REVERSAL' for r in linked)
  group['period_net_revenue_cop']=None if economics is None else format(net,'.2f')
  group['crm_conversion_fraction']=format(Decimal(group['crm_customers'])/group['contacts'],'.6f')
 return {'economic_period':{'since':since,'until':until},'sale_link_basis':'VERIFIED_MODULE_JOURNAL_CONTACT_TO_CURRENT_CONSENTED_CAPTURE_NOT_PROVIDER_PROOF','groups':list(groups.values()),'unattributed_active_contacts':missing,'excluded_withdrawn_contacts':withdrawn,'page_views_measured':False,'causal_attribution_claimed':False,'time_basis':'CURRENT_CONSENT_AND_CURRENT_CRM_STATUS'}
