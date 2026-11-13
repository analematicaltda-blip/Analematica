"""Fixed authenticated native ledger peer. No caller-selected URL, credentials persisted or fallback ledger."""
import os,json,ssl,re,ipaddress
from urllib.parse import urlsplit
from http.cookies import SimpleCookie
from datetime import datetime,timezone
import httpx
from .crm import CRMError
from .source_protocol import wrap,verify
class Bridge:
    def __init__(self,crm,request):self.crm,self.request=crm,request
    def context(self):
        access=self.crm.authorize()
        if not access.principal.get('is_manager'):raise CRMError('LOCAL_ADMINISTRATOR_REQUIRED',403)
        return {'system':'sga-cd','scope':self.crm.store.scope,'actor':self.crm.actor,'role_fingerprint':access.session()['local_role_fingerprint'],'issued_at':datetime.now(timezone.utc).isoformat()}
    def settings(self):
        value=os.environ.get('COMMERCIAL_SALES_LEDGER_ORIGIN','');system=os.environ.get('COMMERCIAL_SALES_LEDGER_SYSTEM','erp-tur')
        try:
            u=urlsplit(value);port=u.port
            if system not in ('erp-tur','analematica') or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('','/'):raise ValueError()
            if u.scheme!='https':
                if u.scheme!='http' or os.environ.get('COMMERCIAL_SALES_ALLOW_LOOPBACK_TESTS')!='1' or not ipaddress.ip_address(u.hostname).is_loopback:raise ValueError()
        except (ValueError,TypeError):raise CRMError('SALE_LEDGER_PEER_REQUIRED',503) from None
        prefix='/api/v1/mi-negocio/comercial/unified/' if system=='erp-tur' else '/api/v1/commercial-unified/'
        cookie='sgacd_'+system.replace('-','_');return value.rstrip('/'),prefix,(cookie+'_session',cookie+'_csrf')
    def client(self):
        origin,prefix,names=self.settings();context=ssl.create_default_context();extra=os.environ.get('COMMERCIAL_SALES_LEDGER_CA_FILE')
        if extra:context.load_verify_locations(extra)
        cookies={k:v for k,v in self.request.cookies.items() if k in names}
        headers={'Accept':'application/json','Accept-Encoding':'identity','Origin':origin,'Referer':origin+'/'}
        auth=self.request.headers.get('x-native-ledger-authorization','')
        if auth.startswith('Bearer ') and len(auth)<8192:headers['Authorization']=auth
        return httpx.Client(base_url=origin,headers=headers,cookies=cookies,verify=context,trust_env=False,follow_redirects=False,timeout=10),prefix,names,bool(auth.startswith('Bearer '))
    def fetch(self,client,method,path,**options):
        try:
            with client.stream(method,path,**options) as response:
                raw=bytearray()
                for chunk in response.iter_bytes():
                    if len(raw)+len(chunk)>524288:raise CRMError('SALE_LEDGER_RESPONSE_LIMIT',503)
                    raw.extend(chunk)
                if response.status_code>=300:raise CRMError('SALE_LEDGER_AUTH_REQUIRED' if response.status_code in (401,403) else 'SALE_LEDGER_RESULT_UNCERTAIN',503)
                try:data=json.loads(raw)
                except (ValueError,UnicodeError):raise CRMError('SALE_LEDGER_RESULT_UNCERTAIN',503) from None
                return data,response.headers
        except httpx.HTTPError:raise CRMError('SALE_LEDGER_RESULT_UNCERTAIN',503) from None
    def csrf(self,client,prefix,bearer):
        if bearer:return
        data,headers=self.fetch(client,'GET',prefix+'crm/session/status/')
        if not isinstance(data,dict) or not isinstance(data.get('csrf_token'),str):raise CRMError('SALE_LEDGER_AUTH_REQUIRED',503)
        client.headers['X-CSRFToken']=data['csrf_token']
    def rpc(self,action,body,provider=None):
        context=self.context();packet=wrap(context,body);client,prefix,names,bearer=self.client()
        with client:
            self.csrf(client,prefix,bearer);data,headers=self.fetch(client,'POST',prefix+'sale-source/'+action+'/',params={'provider_id':provider} if provider else {},json=packet)
        try:received,payload=verify(data)
        except CRMError:raise CRMError('SALE_LEDGER_CONTEXT_MISMATCH',503) from None
        if received!=context:raise CRMError('SALE_LEDGER_CONTEXT_MISMATCH',503)
        return payload
    def session(self,action,body=None):
        self.context()
        if action not in ('status','login','mfa','logout'):raise CRMError('INVALID_LEDGER_SESSION_ACTION')
        client,prefix,names,bearer=self.client()
        with client:
            if action!='status':self.csrf(client,prefix,False)
            data,headers=self.fetch(client,'GET' if action=='status' else 'POST',prefix+'crm/session/'+action+'/',**({'json':body} if action!='status' else {}))
            # Forward only this peer's host-bound native session/CSRF cookies.
            cookies=[]
            for cookie in client.cookies.jar:
                if cookie.name not in names:continue
                raw=SimpleCookie();raw[cookie.name]=cookie.value;raw[cookie.name]['path']='/api/';raw[cookie.name]['httponly']=True;raw[cookie.name]['samesite']='Strict'
                if self.request.url.scheme=='https' or self.request.headers.get('x-forwarded-proto')=='https':raw[cookie.name]['secure']=True
                cookies.append(raw[cookie.name].OutputString())
        return data,cookies
