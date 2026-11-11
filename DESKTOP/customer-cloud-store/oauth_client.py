"""Customer-native OAuth/PKCE. Tokens live in memory, never in ERP or disk.

Requires a legitimately registered native/public client and exact loopback redirect.
Live provider qualification is separate from mocked protocol tests.
"""
import base64,hashlib,secrets,time,re
from dataclasses import dataclass,field
from urllib.parse import urlencode,urlsplit,parse_qs
import httpx

PROVIDERS={
 'google_drive':{'authorize':'https://accounts.google.com/o/oauth2/v2/auth','token':'https://oauth2.googleapis.com/token','scope':'https://www.googleapis.com/auth/drive.file'},
 'onedrive':{'authorize':'https://login.microsoftonline.com/common/oauth2/v2.0/authorize','token':'https://login.microsoftonline.com/common/oauth2/v2.0/token','scope':'https://graph.microsoft.com/Files.ReadWrite.AppFolder'},
}
class OAuthError(ValueError):pass

def bounded_request(client,method,url,*,maximum=65536,anonymous=False,**kwargs):
    """No redirects; bound response bodies and never echo provider error contents."""
    request=client.build_request(method,url,**kwargs)
    if anonymous:
        for header in ("authorization","cookie","proxy-authorization"):
            request.headers.pop(header,None)
    response=client.send(request,stream=True,follow_redirects=False,auth=None)
    try:
        data=bytearray()
        for chunk in response.iter_bytes(chunk_size=16384):
            if len(data)+len(chunk)>maximum:raise OAuthError('Provider response exceeds supported size.')
            data.extend(chunk)
        return response.status_code,bytes(data)
    finally:response.close()

@dataclass(repr=False)
class AccessSession:
    provider:str
    _token:str=field(repr=False)
    expires_at:float
    clock:object=field(default=time.monotonic,repr=False)
    revoked:bool=False
    def __repr__(self):return f'AccessSession(provider={self.provider!r}, credentials=REDACTED)'
    def bearer(self):
        if self.revoked or self.clock()>=self.expires_at:raise OAuthError('Customer authorization expired or revoked; authorize again.')
        return 'Bearer '+self._token
    def forget(self):self._token='';self.revoked=True

class NativeOAuth:
    def __init__(self,provider,client_id,redirect_uri,*,client=None,clock=time.monotonic):
        if provider not in PROVIDERS or not isinstance(client_id,str) or not re.fullmatch('[A-Za-z0-9._-]{10,250}',client_id):raise OAuthError('Registered public/native client required.')
        u=urlsplit(redirect_uri)
        if u.scheme!='http' or u.hostname!='127.0.0.1' or u.username or u.password or u.query or u.fragment or u.path!='/oauth/callback' or u.port is None or not 1024<=u.port<=65535:raise OAuthError('Exact registered loopback callback required.')
        self.provider=provider;self.client_id=client_id;self.redirect_uri=redirect_uri;self.clock=clock;self.client=client or httpx.Client(timeout=httpx.Timeout(15,connect=5),trust_env=False,follow_redirects=False);self._owns=client is None
        self._state=None;self._verifier=None;self._deadline=0
    def close(self):
        self._state=self._verifier=None
        if self._owns:self.client.close()
    def begin(self):
        self._state=secrets.token_urlsafe(32);self._verifier=secrets.token_urlsafe(48);self._deadline=self.clock()+300
        challenge=base64.urlsafe_b64encode(hashlib.sha256(self._verifier.encode('ascii')).digest()).rstrip(b'=').decode()
        p=PROVIDERS[self.provider];query={'client_id':self.client_id,'redirect_uri':self.redirect_uri,'response_type':'code','scope':p['scope'],'state':self._state,'code_challenge':challenge,'code_challenge_method':'S256'}
        if self.provider=='google_drive':query['access_type']='online'
        return p['authorize']+'?'+urlencode(query)
    def finish(self,callback_url):
        if not self._state or self.clock()>=self._deadline:raise OAuthError('Authorization session expired or already consumed.')
        if not isinstance(callback_url,str) or len(callback_url)>16384:raise OAuthError('Bounded authorization callback required.')
        actual=urlsplit(callback_url);expected=urlsplit(self.redirect_uri)
        if (actual.scheme,actual.netloc,actual.path)!=(expected.scheme,expected.netloc,expected.path) or actual.fragment:raise OAuthError('Callback destination differs from registered redirect.')
        values=parse_qs(actual.query,keep_blank_values=True)
        if any(len(v)!=1 for v in values.values()) or set(values)-{'code','state','scope','authuser','prompt','hd','session_state','error','error_description','error_uri'} or not isinstance(values.get('state',[None])[0],str) or not secrets.compare_digest(values['state'][0],self._state):raise OAuthError('Authorization callback state mismatch.')
        verifier=self._verifier;self._state=self._verifier=None
        if 'error' in values or not values.get('code',[''])[0] or len(values['code'][0])>8192:raise OAuthError('Provider authorization was denied or incomplete.')
        profile=PROVIDERS[self.provider]
        data={'grant_type':'authorization_code','client_id':self.client_id,'redirect_uri':self.redirect_uri,'code':values['code'][0],'code_verifier':verifier}
        if self.provider=='onedrive':data['scope']=profile['scope']
        try:status,raw=bounded_request(self.client,'POST',profile['token'],data=data)
        except (httpx.HTTPError,OAuthError):raise OAuthError('Token exchange unconfirmed; begin a new authorization, do not reuse the code.') from None
        if status!=200:raise OAuthError('Provider did not authorize this registered client.')
        try:token=__import__('json').loads(raw)
        except (ValueError,UnicodeError):raise OAuthError('Invalid provider token response.') from None
        if not isinstance(token,dict) or not isinstance(token.get('token_type'),str) or token.get('token_type','').lower()!='bearer' or not isinstance(token.get('access_token'),str) or not re.fullmatch('[\x21-\x7e]{20,16384}',token['access_token']) or type(token.get('expires_in')) is not int or not 1<=token['expires_in']<=86400:raise OAuthError('Unsupported bounded access token.')
        scope=token.get('scope')
        if scope is not None:
            if not isinstance(scope,str):raise OAuthError('Invalid granted scope.')
            scopes={s.removeprefix('https://graph.microsoft.com/') for s in scope.split()};wanted={profile['scope'].removeprefix('https://graph.microsoft.com/')}
            if scopes!=wanted:raise OAuthError('Grant exceeds or lacks the requested minimal scope.')
        # Refresh/ID tokens are deliberately not stored or returned.
        return AccessSession(self.provider,token['access_token'],self.clock()+token['expires_in'],self.clock)
