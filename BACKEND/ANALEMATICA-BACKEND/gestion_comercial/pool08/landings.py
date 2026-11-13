"""Owned structured landing builder. No arbitrary HTML, scripts, cross-tenant assets or DNS mutation."""
import json,uuid,re,html
from datetime import datetime,timezone
from urllib.parse import urlsplit
from .crm import CRMError,digest,text
from .opportunities import uuid_ref
TEMPLATES={'SERVICIOS':'Servicios empresariales','TURISMO':'Experiencias turísticas','CULTURA':'Programación cultural','DEPORTES':'Actividades deportivas'}
HEADERS={'Cache-Control':'no-store','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY'}
def content(data):
    if not isinstance(data,dict) or set(data)-{'brand','title','description','template','blocks','capture'} or not {'brand','title','description','template','blocks'}<=set(data):raise CRMError('INVALID_LANDING_CONTENT')
    if not isinstance(data['template'],str) or data['template'] not in TEMPLATES:raise CRMError('INVALID_LANDING_TEMPLATE')
    blocks=data['blocks']
    if not isinstance(blocks,list) or not 1<=len(blocks)<=12:raise CRMError('LANDING_BLOCK_LIMIT')
    result={k:text(data[k],120 if k!='description' else 300) for k in ('brand','title','description')};result['template']=data['template'];result['blocks']=[]
    for block in blocks:
        if not isinstance(block,dict) or set(block)!={'kind','heading','body','url','label'} or block['kind'] not in ('HERO','TEXT','CTA'):raise CRMError('INVALID_LANDING_BLOCK')
        value={'kind':block['kind'],'heading':text(block['heading'],120),'body':text(block['body'],2000,True),'url':'','label':''}
        if block['kind']=='CTA':
            url=text(block['url'],500)
            try:p=urlsplit(url)
            except ValueError:raise CRMError('INVALID_LANDING_LINK') from None
            if p.scheme!='https' or not p.hostname or p.username or p.password or any(c.isspace() or ord(c)<32 for c in url) or '\\' in url:raise CRMError('INVALID_LANDING_LINK')
            try:
                if p.port not in (None,443):raise ValueError()
            except ValueError:raise CRMError('INVALID_LANDING_LINK') from None
            value.update(url=url,label=text(block['label'],80))
        elif block['url'] or block['label']:raise CRMError('INVALID_LANDING_BLOCK')
        result['blocks'].append(value)
    if data.get('capture') is not None:
        from .landing_capture import capture_config
        result['capture']=capture_config(data['capture'])
    return result

def validate_document(item,event):
    if not event or event.get('event_digest')!=digest({k:v for k,v in event.items() if k!='event_digest'}) or item.get('last_event_digest')!=event['event_digest'] or event.get('result_digest')!=digest({k:v for k,v in item.items() if k!='last_event_digest'}):raise CRMError('LANDING_INTEGRITY_REVIEW_REQUIRED',503)

def render(value,preview=False):
    c=content(value);e=lambda s:html.escape(s,quote=True)
    sections=[]
    for b in c['blocks']:
        link='<a rel="noopener noreferrer" href="'+e(b['url'])+'">'+e(b['label'])+'</a>' if b['kind']=='CTA' else ''
        sections.append('<section><h2>'+e(b['heading'])+'</h2><p>'+e(b['body'])+'</p>'+link+'</section>')
    if preview and c.get('capture'):
        sections.append('<section><h2>Solicita información</h2><p>'+e(c['capture']['notice'])+'</p><p>Vista previa: este formulario no envía datos.</p><fieldset disabled><label>Nombre<input></label><label>Correo<input type="email"></label><label><input type="checkbox">Acepto el tratamiento descrito para atender mi solicitud</label><label><input type="checkbox">Deseo recibir comunicaciones comerciales (opcional)</label><button>Enviar solicitud</button></fieldset></section>')
    return '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(c['title'])+'</title><meta name="description" content="'+e(c['description'])+'"><style>body{margin:0;background:linear-gradient(135deg,#071b34,#16466d);color:#fff;font:18px system-ui;line-height:1.6}main{max-width:1000px;margin:auto;padding:24px;overflow-wrap:anywhere}section{border:1px solid #75c9ff;padding:24px;margin:24px 0;border-radius:14px}a{color:#9edaff}a:focus{outline:3px solid #9edaff}p{white-space:pre-wrap}</style></head><body><main>'+('<p>VISTA PREVIA · Sin publicar</p>' if preview else '')+'<header><p>'+e(TEMPLATES[c['template']])+'</p><p>'+e(c['brand'])+'</p><h1>'+e(c['title'])+'</h1><p>'+e(c['description'])+'</p></header>'+''.join(sections)+'</main></body></html>'

def public_html(store,db,ref):
    uuid_ref(ref);row=store.public(db,ref)
    if not row:raise CRMError('LANDING_NOT_FOUND',404)
    item,checksum,event=row
    if digest(item)!=checksum:raise CRMError('LANDING_INTEGRITY_REVIEW_REQUIRED',503)
    validate_document(item,event)
    if item['published_version'] is None:raise CRMError('LANDING_NOT_FOUND',404)
    v=next((x for x in item['versions'] if x['number']==item['published_version']),None)
    if not v or digest(v['content'])!=v['digest']:raise CRMError('LANDING_INTEGRITY_REVIEW_REQUIRED',503)
    return render(v['content'])

class Landings:
    def __init__(self,store,crm):self.store,self.crm,self.actor=store,crm,crm.actor
    def authorize(self):
        if not self.crm.authorize().principal['is_manager']:raise CRMError('LOCAL_ADMINISTRATOR_REQUIRED',403)
    def get(self,ref):
        self.authorize();uuid_ref(ref);item=self.store.get(ref)
        if not item:raise CRMError('LANDING_NOT_FOUND',404)
        validate_document(item,self.store.last_event(ref));return item
    def list(self,offset=0,limit=30):
        self.authorize()
        if type(offset)!=int or not 0<=offset<=100000 or type(limit)!=int or not 1<=limit<=50:raise CRMError('INVALID_PAGE')
        rows,more=self.store.list('','',offset,limit)
        for row in rows:validate_document(row,self.store.last_event(row['id']))
        return {'pages':[{k:row[k] for k in ('id','code','title','revision','status','published_version')} for row in rows],'next_offset':offset+limit if more else None,'truncated':more,'templates':TEMPLATES,'publication_is_local_application':True,'custom_domain_configured':False}
    def receipt(self,rid):
        self.authorize();uuid_ref(rid);event=self.store.event(rid)
        if not event or event['scope']!=self.store.scope or event['actor']!=self.actor or event.get('provider_ref')!=getattr(self.store,'provider',None):raise CRMError('RECEIPT_NOT_FOUND',404)
        if event['event_digest']!=digest({k:v for k,v in event.items() if k!='event_digest'}):raise CRMError('LANDING_INTEGRITY_REVIEW_REQUIRED',503)
        return {**event['receipt'],'previous_receipt_only':True}
    def history(self,ref):
        item=self.get(ref);events=list(self.store.events(ref));previous='0'*64
        for event in events:
            if event['previous_event_digest']!=previous or event['event_digest']!=digest({k:v for k,v in event.items() if k!='event_digest'}):raise CRMError('LANDING_HISTORY_REVIEW_REQUIRED',503)
            previous=event['event_digest']
        if previous!=item['last_event_digest'] or len(events)!=item['revision']:raise CRMError('LANDING_HISTORY_REVIEW_REQUIRED',503)
        if self.store.get(ref)['revision']!=item['revision']:raise CRMError('REVISION_CONFLICT',409)
        return {'events':events,'history_verified':True}
    def preview(self,ref):
        return render(self.get(ref)['versions'][-1]['content'],True)
    def command(self,body):
        self.authorize()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','landing_id','expected_revision','data'}:raise CRMError('INVALID_LANDING_COMMAND')
        rid=uuid_ref(body['request_id']);op=body['operation'];ref=body['landing_id'];rev=body['expected_revision'];data=body['data']
        if type(rev)!=int or not 0<=rev<2**31 or not isinstance(data,dict) or len(json.dumps(data).encode())>14000:raise CRMError('INVALID_LANDING_COMMAND')
        signature=digest({'domain':'LANDING','scope':self.store.scope,'actor':self.actor,'provider_ref':getattr(self.store,'provider',None),'body':body})
        with self.store.transaction():
            self.authorize();self.store.lock();prior=self.store.event(rid)
            if prior:
                if prior['fingerprint']!=signature:raise CRMError('REQUEST_CONFLICT',409)
                return self.receipt(rid)|{'replayed':True}
            previous='0'*64
            if op=='create':
                if ref is not None or rev!=0 or set(data)!={'slug','content'}:raise CRMError('INVALID_LANDING_CREATE')
                slug=data['slug']
                if not isinstance(slug,str) or not re.fullmatch('[a-z0-9][a-z0-9-]{2,79}',slug):raise CRMError('INVALID_LANDING_SLUG')
                if self.store.find_code(slug):raise CRMError('LANDING_SLUG_CONFLICT',409)
                item={'id':str(uuid.uuid4()),'code':slug,'title':content(data['content'])['title'],'revision':0,'versions':[],'approved_digest':None,'published_version':None,'status':'DRAFT'}
            else:
                item=json.loads(json.dumps(self.get(ref)));self.history(ref)
                if item['revision']!=rev:raise CRMError('REVISION_CONFLICT',409)
                previous=item['last_event_digest']
                if rev>=200 and not (op=='unpublish' and item['published_version'] is not None):raise CRMError('LANDING_REVISION_LIMIT',409)
            if op in ('create','edit','restore'):
                if len(item['versions'])>=20:raise CRMError('LANDING_VERSION_LIMIT',409)
                if op=='edit' and set(data)!={'content'}:raise CRMError('INVALID_LANDING_CONTENT')
                restored=None
                if op=='restore':
                    if set(data)!={'version'} or type(data['version'])!=int:raise CRMError('INVALID_LANDING_VERSION')
                    restored=next((x for x in item['versions'] if x['number']==data['version']),None)
                    if not restored:raise CRMError('LANDING_VERSION_NOT_FOUND',404)
                    value=content(restored['content'])
                else:value=content(data['content'])
                item['versions'].append({'number':len(item['versions'])+1,'content':value,'digest':digest(value),'restored_from':restored['number'] if restored else None});item['title']=value['title'];item['approved_digest']=None
            elif op=='approve':
                if data!={'confirmed':True} or type(data['confirmed'])!=bool:raise CRMError('LANDING_APPROVAL_REQUIRED')
                item['approved_digest']=item['versions'][-1]['digest']
            elif op=='publish':
                if data!={'confirmed':True} or type(data['confirmed'])!=bool:raise CRMError('LANDING_PUBLICATION_REQUIRED')
                if item['approved_digest']!=item['versions'][-1]['digest']:raise CRMError('LANDING_APPROVAL_STALE',409)
                capture=item['versions'][-1]['content'].get('capture')
                if capture and capture.get('offer_ref'):
                    from .pricing_store import Store as PriceStore
                    from .crm import moment
                    from .pricing import Pricing
                    try:offer=Pricing(PriceStore(self.crm.store),self.crm).get(capture['offer_ref'])
                    except CRMError as exc:
                        if exc.status==404:raise CRMError('FORM_OFFER_UNAVAILABLE',409) from None
                        raise
                    if not offer or offer['status']!='ACTIVE' or not moment(offer['valid_from'])<=datetime.now(timezone.utc)<=moment(offer['valid_until']):raise CRMError('FORM_OFFER_UNAVAILABLE',409)
                item['published_version']=item['versions'][-1]['number'];item['publisher_ref']=self.actor;item['status']='PUBLISHED'
            elif op=='unpublish':
                if data!={'confirmed':True} or type(data['confirmed'])!=bool:raise CRMError('LANDING_WITHDRAWAL_REQUIRED')
                item['published_version']=None;item['approved_digest']=None;item['status']='DRAFT'
            else:raise CRMError('INVALID_LANDING_OPERATION')
            item['revision']+=1
            receipt={'landing_id':item['id'],'revision':item['revision'],'status':item['status'],'published_version':item['published_version'],'content_version':item['versions'][-1]['number'],'replayed':False}
            event={'id':rid,'scope':self.store.scope,'actor':self.actor,'provider_ref':getattr(self.store,'provider',None),'item_id':item['id'],'operation':op,'fingerprint':signature,'previous_event_digest':previous,'created_at':datetime.now(timezone.utc).isoformat(),'result_digest':digest({k:v for k,v in item.items() if k!='last_event_digest'}),'receipt':receipt}
            event['event_digest']=digest(event);item['last_event_digest']=event['event_digest'];self.store.save(item,rev);self.store.append(event);return receipt
