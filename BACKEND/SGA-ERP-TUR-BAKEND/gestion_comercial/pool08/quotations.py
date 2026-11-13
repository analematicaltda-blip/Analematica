"""Versioned proposals. Link possession is never verified customer identity or payment."""
import uuid,copy,hmac,hashlib,os,re
from datetime import datetime,timezone,timedelta
from decimal import Decimal
from .crm import CRMError,text,moment,digest
from .opportunities import uuid_ref,FALSE_FINANCIAL
from .pricing import integer
FALSE_EFFECTS={**FALSE_FINANCIAL,'reservation_created':False,'capacity_reserved':False}
def link_key():
    value=os.environ.get('COMMERCIAL_QUOTE_LINK_KEY','')
    if len(value)<32:raise CRMError('QUOTE_LINK_KEY_REQUIRED',503)
    return value.encode()
class Quotations:
    def __init__(self,store,crm,pricing,capacity,media):self.store,self.crm,self.pricing,self.capacity,self.media,self.actor=store,crm,pricing,capacity,media,crm.actor
    def authority(self,manager=False):return self.pricing.authority(manage=manager)
    def verify(self,item):
        if item['status']!='CAPACITY_POLICY' and digest(item['content'])!=item['content_digest']:raise CRMError('QUOTE_CONTENT_DIGEST_MISMATCH',503)
        event=self.store.last_event(item['id'])
        if not event or event['event_digest']!=item['last_event_digest'] or digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest'] or event['result_digest']!=digest({k:v for k,v in item.items() if k!='last_event_digest'}):raise CRMError('QUOTE_INTEGRITY_REVIEW_REQUIRED',503)
    def get(self,ref):
        self.authority();uuid_ref(ref);item=self.store.get(ref)
        if item is None:raise CRMError('QUOTE_NOT_FOUND',404)
        self.verify(item);return item
    def list(self,q='',offset=0,limit=30):
        self.authority();integer(offset,0,100000,'INVALID_PAGE');integer(limit,1,100,'INVALID_PAGE')
        if not isinstance(q,str) or len(q)>200:raise CRMError('INVALID_PAGE')
        rows,more=self.store.list(q,'',offset,limit)
        for row in rows:self.verify(row)
        summaries=[{**{k:row[k] for k in ('id','title','status','version','revision')},'expires_at':row['content']['expires_at'],'total':row['content']['estimate']['total'],'currency':row['content']['estimate']['currency']} for row in rows]
        return {'quotations':summaries,'next_offset':offset+limit if more else None,'context':{'actor_ref':self.actor,'tenant_ref':self.store.scope},**FALSE_EFFECTS}
    def history(self,ref,offset=0):
        item=self.get(ref);integer(offset,0,100000,'INVALID_PAGE');previous='0'*64;events=[]
        for event in self.store.events(ref):
            if event['previous_event_digest']!=previous or digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest']:raise CRMError('QUOTE_HISTORY_REVIEW_REQUIRED',503)
            previous=event['event_digest'];events.append(event)
        current=self.store.get(ref)
        if current['revision']!=item['revision']:raise CRMError('HISTORY_CHANGED_RETRY',409)
        if previous!=current['last_event_digest']:raise CRMError('QUOTE_HISTORY_REVIEW_REQUIRED',503)
        return {'events':events[offset:offset+2],'next_offset':offset+2 if len(events)>offset+2 else None,'history_verified':True}
    def policy(self,item_id,revision):
        value=self.store.policy(item_id,revision)
        if value is None:raise CRMError('CAPACITY_POLICY_REVIEW_REQUIRED',409)
        self.verify(value);self.history(value['id']);return value
    def inspect_capacity(self,content):
        now=datetime.now(timezone.utc);windows=content['service_windows'];by_id={w['item_id']:w for w in windows};required=set();groups={};policies=[]
        for line in content['estimate']['lines']:
            policy=self.policy(line['item_id'],line['revision']);policies.append({'policy_id':policy['id'],'event_digest':policy['last_event_digest'],'mode':policy['mode'],'item_id':line['item_id']})
            if policy['mode']=='NOT_APPLICABLE':continue
            required.add(line['item_id']);window=by_id.get(line['item_id'])
            if window is None:raise CRMError('SERVICE_WINDOW_REQUIRED')
            start,end=moment(window['start_at']),moment(window['end_at']);q=Decimal(line['quantity'])
            if q!=q.to_integral_value() or not 0<q<=10000 or not now<start<end or end-start>timedelta(days=365):raise CRMError('INVALID_SERVICE_WINDOW')
            groups.setdefault(policy['resource_ref'],[]).append((start,end,int(q)))
        if set(by_id)!=required:raise CRMError('UNEXPECTED_SERVICE_WINDOW')
        checks=[]
        for ref,ranges in groups.items():
            events=[]
            for start,end,q in ranges:events.extend([(start,q),(end,-q)])
            active=peak=0
            for _,n in sorted(events,key=lambda e:(e[0],e[1])):active+=n;peak=max(peak,active)
            result=self.capacity.inspect(ref,min(x[0] for x in ranges),max(x[1] for x in ranges),peak)
            if not result['available']:raise CRMError('CAPACITY_NOT_AVAILABLE',409)
            checks.append(result)
        return {'policies':policies,'checks':checks,'checked_at':now.isoformat(),'reserved':False,'semantics':'CONSERVATIVE_BOUNDING_INTERVAL_POINT_IN_TIME'}
    def content(self,data):
        if set(data)!={'title','contact_id','opportunity_id','offer','terms','expires_at','media_ids','service_windows'}:raise CRMError('INVALID_QUOTE_FIELDS')
        contact=self.crm.get(data['contact_id'])
        if contact['status']=='WITHDRAWN':raise CRMError('CONTACT_WITHDRAWN',409)
        opp=data['opportunity_id']
        if opp is not None:
            from .opportunities import Opportunities
            from .opportunity_store import Store
            value=Opportunities(Store(self.crm.store),self.crm).get(opp)
            if value.get('requires_adoption') or value['contact_id']!=contact['id'] or value['stage']=='LOST':raise CRMError('OPPORTUNITY_CONTACT_MISMATCH',409)
        if not isinstance(data['media_ids'],list) or len(data['media_ids'])>5 or len(set(map(str,data['media_ids'])))!=len(data['media_ids']):raise CRMError('INVALID_QUOTE_MEDIA')
        media=[self.media.get(uuid_ref(ref)) for ref in data['media_ids']]
        windows=data['service_windows']
        if not isinstance(windows,list) or len(windows)>30:raise CRMError('INVALID_SERVICE_WINDOW')
        ids=set()
        for window in windows:
            if not isinstance(window,dict) or set(window)!={'item_id','start_at','end_at'}:raise CRMError('INVALID_SERVICE_WINDOW')
            ref=uuid_ref(window['item_id'])
            if ref in ids:raise CRMError('DUPLICATE_SERVICE_WINDOW')
            ids.add(ref);moment(window['start_at']);moment(window['end_at'])
        if not isinstance(data['offer'],dict) or not isinstance(data['offer'].get('lines'),list) or not 1<=len(data['offer']['lines'])<=10:raise CRMError('INVALID_OFFER')
        estimate=self.pricing.estimate(data['offer']);now=datetime.now(timezone.utc);requested=moment(data['expires_at']);expiry=min(requested,moment(estimate['expires_at']))
        if not now<expiry<=now+timedelta(days=30):raise CRMError('INVALID_QUOTE_EXPIRY')
        if windows:expiry=min(expiry,*(moment(w['start_at']) for w in windows))
        if expiry<=now:raise CRMError('INVALID_QUOTE_EXPIRY')
        return {'title':text(data['title'],200),'contact_id':contact['id'],'opportunity_id':opp,'offer':copy.deepcopy(data['offer']),'estimate':estimate,'terms':text(data['terms'],4000),'expires_at':expiry.isoformat(),'media':media,'service_windows':copy.deepcopy(windows),'company_ref':self.store.scope,'company_name':self.crm.store.company_name}
    def revalidate(self,item):
        content=item['content'];contact=self.crm.get(content['contact_id'])
        if contact['status']=='WITHDRAWN':raise CRMError('CONTACT_WITHDRAWN',409)
        if datetime.now(timezone.utc)>=moment(content['expires_at']):raise CRMError('QUOTE_EXPIRED',409)
        if content['opportunity_id']:
            from .opportunities import Opportunities
            from .opportunity_store import Store
            opportunity=Opportunities(Store(self.crm.store),self.crm).get(content['opportunity_id'])
            if opportunity['stage']=='LOST' or opportunity['contact_id']!=content['contact_id']:raise CRMError('OPPORTUNITY_CONTACT_MISMATCH',409)
        estimate=self.pricing.estimate(content['offer'])
        if (estimate['total'],estimate['lines'])!=(content['estimate']['total'],content['estimate']['lines']):raise CRMError('QUOTE_PRICE_REVIEW_REQUIRED',409)
        for media in content['media']:
            if self.media.get(media['id'])!=media:raise CRMError('QUOTE_MEDIA_CHANGED',409)
        return self.inspect_capacity(content)
    def token(self,ref,lid,version,content_digest):return hmac.new(link_key(),('quote-link-v1|'+self.store.scope+'|'+ref+'|'+lid+'|'+str(version)+'|'+content_digest).encode(),hashlib.sha256).hexdigest()
    def receipt(self,rid):
        self.authority();uuid_ref(rid);event=self.store.event(rid)
        if not event or event['scope']!=self.store.scope or event['actor']!=self.actor:raise CRMError('QUOTE_RECEIPT_NOT_FOUND',404)
        if digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest']:raise CRMError('QUOTE_INTEGRITY_REVIEW_REQUIRED',503)
        result=copy.deepcopy(event['receipt'])
        if result.get('link_id'):result['link_token']=self.token(result['quotation_id'],result['link_id'],event['snapshot']['version'],event['snapshot']['content_digest'])
        return result
    def save_event(self,item,rid,operation,data,fingerprint,prior,actor=None,receipt=None):
        item['updated_at']=datetime.now(timezone.utc).isoformat();item['revision']=prior+1
        result=digest({k:v for k,v in item.items() if k!='last_event_digest'})
        receipt=receipt or {'quotation_id':item['id'],'revision':item['revision'],'version':item.get('version'),'status':item['status'],'replayed':False,**FALSE_EFFECTS}
        event={'id':rid,'scope':self.store.scope,'actor':actor or self.actor,'item_id':item['id'],'operation':operation,'fingerprint':fingerprint,'previous_event_digest':item.get('last_event_digest','0'*64),'result_digest':result,'data':data,'snapshot':copy.deepcopy({k:v for k,v in item.items() if k!='last_event_digest'}),'receipt':receipt}
        event['event_digest']=digest(event);item['last_event_digest']=event['event_digest'];self.store.save(item,prior);self.store.append(event);return receipt
    def command(self,body):
        self.authority()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','quotation_id','expected_revision','data'} or not isinstance(body['data'],dict):raise CRMError('INVALID_COMMAND')
        rid=uuid_ref(body['request_id']);op=body['operation'];ref=body['quotation_id'];rev=integer(body['expected_revision'],0,2**31-1,'INVALID_REVISION');data=body['data'];signature=digest({'scope':self.store.scope,'actor':self.actor,'body':body})
        with self.store.transaction():
            self.authority();self.store.lock();prior=self.store.event(rid)
            if prior:
                if prior['fingerprint']!=signature:raise CRMError('REQUEST_CONFLICT',409)
                return self.receipt(rid)|{'replayed':True}
            if op=='review_capacity':
                self.authority(True)
                if ref is not None or rev or set(data)!={'item_id','price_revision','mode','resource_ref','reason','support_digest'}:raise CRMError('INVALID_CAPACITY_POLICY')
                price=self.pricing.get(data['item_id'])
                if type(data['price_revision'])!=int or price['revision']!=data['price_revision']:raise CRMError('PRICE_REVISION_CHANGED',409)
                if data['mode'] not in ('NOT_APPLICABLE','REQUIRED') or not isinstance(data['support_digest'],str) or not re.fullmatch('[a-f0-9]{64}',data['support_digest']):raise CRMError('INVALID_CAPACITY_POLICY')
                text(data['reason'],500)
                if data['mode']=='REQUIRED':self.capacity.resource(data['resource_ref'])
                elif data['resource_ref'] is not None:raise CRMError('INVALID_CAPACITY_POLICY')
                if self.store.policy(price['id'],price['revision']):raise CRMError('CAPACITY_POLICY_IMMUTABLE',409)
                item={**copy.deepcopy(data),'id':str(uuid.uuid4()),'status':'CAPACITY_POLICY','code':'CAP:'+price['id']+':'+str(price['revision']),'title':price['title'],'reviewed_by':self.actor,'reviewed_at':datetime.now(timezone.utc).isoformat(),'external_authenticity_verified':False}
            elif op=='create':
                if ref is not None or rev:raise CRMError('INVALID_COMMAND')
                content=self.content(data);item={'id':str(uuid.uuid4()),'status':'DRAFT','code':'Q-'+rid,'title':content['title'],'version':1,'content':content,'content_digest':digest(content),'links':[],'issuer_ref':self.actor,'provider_ref':getattr(self.store,'provider',None),'acceptance':None,**FALSE_EFFECTS}
            else:
                item=copy.deepcopy(self.get(ref));self.history(ref)
                if item['status']=='CAPACITY_POLICY' or item['revision']!=rev:raise CRMError('REVISION_CONFLICT',409)
                if op=='revise':
                    if item['status'] not in ('DRAFT','ISSUED'):raise CRMError('QUOTE_TERMINAL',409)
                    content=self.content(data);item.update(content=content,content_digest=digest(content),title=content['title'],status='DRAFT',version=item['version']+1,links=[])
                elif op=='issue':
                    if data!={} or item['status']!='DRAFT':raise CRMError('INVALID_QUOTE_TRANSITION',409)
                    item['last_validation']=self.revalidate(item);item['status']='ISSUED'
                elif op=='link':
                    self.authority(True);link_key()
                    if data!={'confirm_share':True} or item['status']!='ISSUED' or len(item['links'])>=10:raise CRMError('INVALID_QUOTE_LINK')
                    self.revalidate(item);item['links'].append({'id':rid,'version':item['version'],'content_digest':item['content_digest'],'expires_at':item['content']['expires_at'],'used_request_id':None})
                elif op=='withdraw':
                    if item['status'] not in ('DRAFT','ISSUED') or set(data)!={'reason'}:raise CRMError('INVALID_QUOTE_TRANSITION',409)
                    item['withdraw_reason']=text(data['reason'],500);item['status']='WITHDRAWN';item['links']=[]
                else:raise CRMError('UNKNOWN_OPERATION')
            receipt=None
            if op=='link':receipt={'quotation_id':item['id'],'link_id':rid,'revision':rev+1,'version':item['version'],'replayed':False}
            result=self.save_event(item,rid,op,data,signature,rev,receipt=receipt)
        return self.receipt(rid)
    def link_view(self,ref,lid,token):
        self.authority();uuid_ref(lid);item=self.get(uuid_ref(ref));self.history(ref)
        link=next((x for x in item.get('links',[]) if x['id']==lid),None)
        if not link or not isinstance(token,str) or not re.fullmatch('[a-f0-9]{64}',token) or not hmac.compare_digest(self.token(ref,lid,link['version'],link['content_digest']),token):raise CRMError('QUOTE_LINK_DENIED',403)
        if not link or link['version']!=item['version'] or link['content_digest']!=item['content_digest'] or datetime.now(timezone.utc)>=moment(link['expires_at']) or item['status'] not in ('ISSUED','ACCEPTED'):raise CRMError('QUOTE_LINK_DENIED',403)
        # Public projection excludes internal identity, audit, issuer, scopes and other links.
        view={k:item[k] for k in ('id','status','version','content_digest','acceptance')};content=item['content'];view['content']={k:content[k] for k in ('title','company_name','terms','expires_at','media')};view['content']['estimate']={k:content['estimate'][k] for k in ('currency','lines','subtotal','discount','tax','total')}
        view['content']['estimate']['lines']=[{k:l[k] for k in ('title','code','quantity','unit_price','discount','base','tax','total')} for l in content['estimate']['lines']]
        view['acceptance']={k:item['acceptance'][k] for k in ('version','content_digest','accepted_at','method','customer_identity_verified')} if item['acceptance'] else None
        view['identity_verified']=False;view.update(FALSE_EFFECTS);return item,link,view
    def accept_link(self,ref,lid,token,body):
        if not isinstance(body,dict) or set(body)!={'request_id','version','content_digest','confirmed'} or body['confirmed'] is not True:raise CRMError('INVALID_ACCEPTANCE')
        rid=uuid_ref(body['request_id']);signature=digest({'link_id':lid,'body':body});actor='LINK_HOLDER:'+lid
        with self.store.transaction():
            self.authority();self.store.lock();item,link,view=self.link_view(ref,lid,token);prior=self.store.event(rid)
            if prior:
                if prior['actor']!=actor or prior['fingerprint']!=signature:raise CRMError('REQUEST_CONFLICT',409)
                return prior['receipt']|{'replayed':True}
            if link['used_request_id'] or item['status']!='ISSUED':raise CRMError('QUOTE_LINK_ALREADY_USED',409)
            if type(body['version'])!=int or body['version']!=item['version'] or body['content_digest']!=item['content_digest']:raise CRMError('QUOTE_VERSION_CHANGED',409)
            validation=self.revalidate(item);item=copy.deepcopy(item);rev=item['revision'];next(x for x in item['links'] if x['id']==lid)['used_request_id']=rid;item['status']='ACCEPTED'
            item['acceptance']={'version':item['version'],'content_digest':item['content_digest'],'accepted_at':datetime.now(timezone.utc).isoformat(),'method':'LINK_POSSESSION','customer_identity_verified':False,'link_id':lid,'validation':validation}
            return self.save_event(item,rid,'accept_link',body,signature,rev,actor=actor)
