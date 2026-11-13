"""Public form ingestion bound to an approved page; never authenticates a prospect's email."""
import json,uuid,hmac,hashlib,base64,time,html
from datetime import datetime,timezone,timedelta
from .crm import CRMError,digest,text,moment
from .opportunities import uuid_ref
from .landings import content,render,HEADERS
UTM=('utm_source','utm_medium','utm_campaign','utm_content','utm_term')
def mac(key,value):return hmac.new(key,value.encode(),hashlib.sha256).hexdigest()
def capture_config(value):
    if value is None:return None
    if not isinstance(value,dict) or set(value)!={'notice','privacy_url','offer_ref'}:raise CRMError('INVALID_CAPTURE_CONFIG')
    from urllib.parse import urlsplit
    notice=text(value['notice'],1000);url=text(value['privacy_url'],500)
    try:p=urlsplit(url);valid=p.scheme=='https' and p.hostname and not p.username and not p.password and p.port in (None,443) and not any(c.isspace() for c in url) and '\\' not in url
    except ValueError:valid=False
    if not valid:raise CRMError('INVALID_PRIVACY_URL')
    if value['offer_ref'] is not None:uuid_ref(value['offer_ref'])
    return {'notice':notice,'privacy_url':url,'offer_ref':value['offer_ref']}
def unpack(key,token):
    try:
        encoded,signature=token.split('.')
        if len(token)>3000 or not hmac.compare_digest(mac(key,'form:'+encoded),signature):raise ValueError()
        value=json.loads(base64.urlsafe_b64decode(encoded+'='*(-len(encoded)%4)))
        if set(value)!={'page','version','nonce','issued','browser','utm'} or type(value['issued'])!=int or not 0<=time.time()-value['issued']<=1800:raise ValueError()
        uuid_ref(value['nonce']);return value
    except (ValueError,TypeError,AttributeError,KeyError):raise CRMError('FORM_PROOF_INVALID_OR_EXPIRED',400) from None
class Capture:
    def __init__(self,store,crm,landings,key):
        self.store,self.crm,self.landings=store,crm,landings
        namespace=digest({'domain':'PUBLIC_LANDING_CAPTURE_V1','system':crm.store.system,'scope':store.scope,'provider':getattr(store,'provider',None)})
        self.key=hmac.new(key,namespace.encode(),hashlib.sha256).digest()
    def page(self,ref,version=None,published=True):
        item=self.landings.get(ref)
        if published and (item['published_version'] is None or version is not None and version!=item['published_version']):raise CRMError('FORM_PAGE_CHANGED_OR_WITHDRAWN',409)
        number=item['published_version'] if version is None else version
        v=next((v for v in item['versions'] if v['number']==number),None)
        if not v:raise CRMError('FORM_VERSION_NOT_FOUND',404)
        config=capture_config(v['content'].get('capture'))
        if not config:raise CRMError('FORM_DISABLED',404)
        if config['offer_ref']:
            from .pricing_store import Store as PriceStore
            from .pricing import Pricing
            try:offer=Pricing(PriceStore(self.crm.store),self.crm).get(config['offer_ref'])
            except CRMError as exc:
                if exc.status==404:raise CRMError('FORM_OFFER_UNAVAILABLE',409) from None
                raise
            if not offer or offer['status']!='ACTIVE' or not moment(offer['valid_from'])<=datetime.now(timezone.utc)<=moment(offer['valid_until']):raise CRMError('FORM_OFFER_UNAVAILABLE',409)
        return item,v,config
    def form(self,ref,browser,utm,action,canonical):
        item,v,config=self.page(ref);safe_utm={k:text(utm.get(k,''),120,True) for k in UTM}
        value={'page':ref,'version':v['number'],'nonce':str(uuid.uuid4()),'issued':int(time.time()),'browser':digest(browser),'utm':safe_utm};encoded=base64.urlsafe_b64encode(json.dumps(value,separators=(',',':')).encode()).decode().rstrip('=');token=encoded+'.'+mac(self.key,'form:'+encoded);e=lambda x:html.escape(x,quote=True)
        form='<section><h2>Solicita información</h2><p>Solicitud comercial; no constituye registro institucional ni inscripción en el RNT.</p><form method="post" action="'+e(action)+'"><input type="hidden" name="token" value="'+e(token)+'"><label>Nombre<input name="name" maxlength="150" required autocomplete="name"></label><label>Correo<input name="email" type="email" maxlength="254" required autocomplete="email"></label><label>Teléfono (opcional)<input name="phone" maxlength="30" autocomplete="tel"></label><label style="display:none">Deja vacío este campo<input name="company_website" tabindex="-1" autocomplete="off"></label><p>'+e(config['notice'])+'</p><a href="'+e(config['privacy_url'])+'" rel="noopener noreferrer">Política de privacidad</a><label><input type="checkbox" name="consent" value="yes" required>Acepto el tratamiento descrito para atender mi solicitud</label><label><input type="checkbox" name="marketing" value="yes">Deseo recibir comunicaciones comerciales (opcional; puedo retirar esta declaración)</label><button>Enviar solicitud</button></form></section>'
        out=render(v['content']).replace('</style>','label{display:block;margin:14px 0}input,button{max-width:100%;box-sizing:border-box;background:#0a243d;color:#fff;border:1px solid #75c9ff;padding:10px}button:focus,input:focus{outline:3px solid #9edaff}</style>');seo='<link rel="canonical" href="'+e(canonical)+'"><meta property="og:title" content="'+e(v['content']['title'])+'"><meta property="og:description" content="'+e(v['content']['description'])+'"><meta property="og:type" content="website">'
        return out.replace('</head>',seo+'</head>').replace('</main>',form+'</main>')
    def verify(self,ref,body,browser):
        if not isinstance(body,dict) or set(body)-{'token','name','email','phone','company_website','consent','marketing'} or not {'token','name','email','consent'}<=set(body):raise CRMError('INVALID_PUBLIC_FORM')
        if body.get('company_website','') or body['consent']!='yes' or body.get('marketing','') not in ('','yes'):raise CRMError('PUBLIC_CONSENT_OR_SPAM_REJECTED')
        proof=unpack(self.key,body['token'])
        if proof['page']!=ref or proof['browser']!=digest(browser):raise CRMError('FORM_PROOF_SCOPE_REJECTED',403)
        return proof
    def submit(self,ref,body,browser,ip):
        proof=self.verify(ref,body,browser);rid=proof['nonce'];fingerprint=digest(body);actor='PUBLIC_LANDING:'+rid
        with self.store.transaction():
            self.crm.authorize();self.store.lock()
            prior=self.store.get(rid)
            if prior:
                self.validate(prior)
                if prior['fingerprint']!=fingerprint:raise CRMError('FORM_REPLAY_CONFLICT',409)
                return self.receipt(prior)
            item,v,config=self.page(ref,proof['version'])
            now=datetime.now(timezone.utc);ip_digest=mac(self.key,'ip:'+self.store.scope+':'+ip)
            if self.store.recent(ip_digest,(now-timedelta(hours=1)).isoformat())>=10:raise CRMError('PUBLIC_FORM_RATE_LIMIT',429)
            values=self.crm.normalized({'name':body['name'],'email':body['email'],'phone':body.get('phone',''),'origin':'LANDING_FORM','responsible_ref':self.crm.actor,'notes':''})
            if not values['email']:raise CRMError('PUBLIC_EMAIL_REQUIRED')
            matches=self.crm.store.duplicates(values['email'],values['phone'],None);contact_id=None;created=not matches
            consent={'processing_granted':True,'marketing_declared':body.get('marketing')=='yes','notice':config['notice'],'privacy_url':config['privacy_url'],'notice_digest':digest(config),'recorded_at':now.isoformat(),'email_ownership_verified':False,'delivery_authorized':False}
            source={'page_id':ref,'page_version':v['number'],'offer_ref':config['offer_ref'],'utm':proof['utm'],'utm_authenticity_verified':False,'capture_id':rid,'institutional_registration_created':False}
            if created:
                contact_id=str(uuid.uuid4());contact={**values,'id':contact_id,'revision':1,'status':'PROSPECT','consents':{},'tasks':[],'duplicate_review':None,'customer_ref':None,'stage':'nuevo','landing_attribution':source}
                for purpose,granted in [('SERVICE',True),('MARKETING',consent['marketing_declared'])]:contact['consents']['EMAIL:'+purpose]={'channel':'EMAIL','purpose':purpose,'granted':granted,'evidence_digest':digest(consent),'expires_at':(now+timedelta(days=365)).isoformat(),'recorded_at':now.isoformat(),'recorded_by':actor,'source_capture':rid,'delivery_authorized':False,'evidence_authenticity_verified':False}
                self.crm.store.save(contact,0);self.crm.store.append(str(uuid.uuid5(uuid.UUID(rid),'crm-create')),actor,'landing_capture',contact_id,fingerprint,{'contact_id':contact_id,'revision':1,'status':'PROSPECT'},{'source':source,'consent':consent,'public_declaration_only':True})
            document={'id':rid,'code':rid,'title':'Captación de landing','revision':1,'status':'CREATED_PROSPECT' if created else 'REVIEW_REQUIRED','fingerprint':fingerprint,'page_id':ref,'page_version':v['number'],'created_at':now.isoformat(),'ip_digest':ip_digest,'created_contact':created,'requires_review':not created,'contact_id':contact_id,'candidate_ids':matches[:20],'submitted_fields':values,'consent':consent,'source':source,'withdrawn_at':None}
            self.write(document,'capture',actor,0);return self.receipt(document)
    def validate(self,item):
        events=list(self.store.events(item['id']));previous='0'*64
        for step in events:
            if not isinstance(step,dict) or step.get('previous_event_digest')!=previous or step.get('event_digest')!=digest({k:v for k,v in step.items() if k!='event_digest'}):raise CRMError('CAPTURE_HISTORY_REVIEW_REQUIRED',503)
            previous=step['event_digest']
        if len(events)!=item['revision']:raise CRMError('CAPTURE_HISTORY_REVIEW_REQUIRED',503)
        event=events[-1] if events else None
        if not event or event['event_digest']!=digest({k:v for k,v in event.items() if k!='event_digest'}) or item['last_event_digest']!=event['event_digest'] or event['result_digest']!=digest({k:v for k,v in item.items() if k!='last_event_digest'}):raise CRMError('CAPTURE_INTEGRITY_REVIEW_REQUIRED',503)
    def write(self,item,operation,actor,expected):
        event={'id':str(uuid.uuid4()),'scope':self.store.scope,'item_id':item['id'],'actor':actor,'operation':operation,'previous_event_digest':item.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in item.items() if k!='last_event_digest'}),'created_at':datetime.now(timezone.utc).isoformat()};event['event_digest']=digest(event);item['last_event_digest']=event['event_digest'];self.store.save(item,expected);self.store.append(event)
    def receipt(self,item):return {'received':True,'reference':item['id'],'withdrawal_proof':mac(self.key,'withdraw:'+item['id']),'withdrawn':bool(item['withdrawn_at']),'email_verified':False,'message_sent':False}
    def withdraw(self,ref,rid,proof):
        uuid_ref(rid)
        if not isinstance(proof,str) or not hmac.compare_digest(proof,mac(self.key,'withdraw:'+rid)):raise CRMError('WITHDRAWAL_PROOF_REQUIRED',403)
        with self.store.transaction():
            self.crm.authorize();self.store.lock();item=self.store.get(rid)
            if not item or item['page_id']!=ref:raise CRMError('CAPTURE_NOT_FOUND',404)
            self.validate(item)
            if item['withdrawn_at']:return {'withdrawn':True,'replayed':True}
            now=datetime.now(timezone.utc).isoformat();contact=self.crm.store.get(item['contact_id']) if item['contact_id'] else None
            if contact and contact.get('landing_attribution',{}).get('capture_id')==rid:
                old=contact['revision'];owned=[c for c in contact['consents'].values() if c.get('source_capture')==rid]
                for c in owned:c['granted']=False
                if old==1 and contact['status']=='PROSPECT' and len(owned)==len(contact['consents']):contact['status']='WITHDRAWN'
                contact['revision']+=1
                self.crm.store.save(contact,old);self.crm.store.append(str(uuid.uuid5(uuid.UUID(rid),'crm-withdraw')),'PUBLIC_LANDING:'+rid,'landing_withdrawal',contact['id'],digest(proof),{'contact_id':contact['id'],'revision':contact['revision'],'status':contact['status']},{'capture_id':rid,'source_declaration_revoked':True,'subsequent_authorizations_preserved':True})
            old=item['revision'];item['revision']+=1;item['status']='WITHDRAWN';item['withdrawn_at']=now;item['consent']['marketing_declared']=False;self.write(item,'withdraw','PUBLIC_LANDING:'+rid,old);return {'withdrawn':True,'replayed':False}
    def metrics(self,ref,offset=0):
        self.landings.get(ref)
        if type(offset)!=int or not 0<=offset<=100000:raise CRMError('INVALID_PAGE')
        rows,more=self.store.by_page(ref,offset,20)
        for row in rows:self.validate(row)
        return {'observed':self.store.metrics(ref),'captures':rows,'next_offset':offset+20 if more else None,'page_views_measured':False,'ad_platform_attribution_verified':False}
