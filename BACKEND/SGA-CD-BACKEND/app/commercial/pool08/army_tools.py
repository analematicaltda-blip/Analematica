"""Real bounded domain reads, never placeholder natural-language tool outputs."""
from collections import Counter
from .crm import CRMError
READ_TOOLS={'crm.contacts':'CRM','crm.opportunities':'CRM','library.assets':'CREATIVE','publishing.queue':'CHANNELS','inbox.queue':'CHANNELS','email.queue':'CHANNELS','mobile.queue':'CHANNELS','ads.plans':'CHANNELS'}
ALIASES={'resumen comercial':list(READ_TOOLS),'revisar contactos':['crm.contacts'],'revisar oportunidades':['crm.opportunities'],'revisar biblioteca':['library.assets'],'revisar publicaciones':['publishing.queue'],'revisar bandeja':['inbox.queue'],'revisar correos':['email.queue'],'revisar mensajería':['mobile.queue'],'revisar pauta':['ads.plans']}
def execute(crm,tool):
 if tool not in READ_TOOLS:raise CRMError('ARMY_DOMAIN_WORKFLOW_REQUIRED',409)
 if tool=='crm.contacts':source=crm.list(limit=20);rows=source['contacts'];more=source['next_offset'] is not None
 elif tool=='crm.opportunities':
  from .opportunities import Opportunities
  from .opportunity_store import Store
  source=Opportunities(Store(crm.store),crm).list(limit=20);rows=source['opportunities'];more=source['next_offset'] is not None
 elif tool=='library.assets':
  from .library_api import service
  source=service(crm).list();rows=source['items'];more=source['next_offset'] is not None
 else:
  from importlib import import_module
  modules={'publishing.queue':('publishing_api','jobs'),'inbox.queue':('inbox_api','threads'),'email.queue':('email_campaign_api','campaigns'),'mobile.queue':('mobile_message_api','jobs'),'ads.plans':('ads_api','campaigns')}
  module,key=modules[tool];source=import_module(__package__+'.'+module).service(crm).list();rows=source[key];more=False
 from .army import digest
 return {'summary':{'sample_count':len(rows),'counts_by_status':dict(Counter(str(r.get('status',r.get('stage','UNKNOWN'))) for r in rows)),'truncated':more,'is_full_population':not more},'source_digest':digest(source),'source_tool':tool,'scope':crm.store.scope,'read_only':True,'provider_success_claimed':False}
