"""Shared OIDC login broker. No provider tokens or application JWTs are persisted."""
from contextlib import contextmanager
import re
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3
import time
from urllib.parse import urlencode, urlparse

import requests
from jose import jwt

MICROSOFT_TENANT='9188040d-6c67-4c5b-b112-36a304b66dad'
PROVIDERS={
 'google':dict(authorize='https://accounts.google.com/o/oauth2/v2/auth',token='https://oauth2.googleapis.com/token',keys='https://www.googleapis.com/oauth2/v3/certs',issuers=['https://accounts.google.com','accounts.google.com']),
 'microsoft':dict(authorize='https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize',token='https://login.microsoftonline.com/consumers/oauth2/v2.0/token',keys='https://login.microsoftonline.com/consumers/discovery/v2.0/keys',issuers=[f'https://login.microsoftonline.com/{MICROSOFT_TENANT}/v2.0'])
}
class SSOError(Exception):
    pass

def provider_config(provider):
    if provider not in PROVIDERS: raise SSOError('Proveedor no disponible')
    prefix='SSO_'+provider.upper()
    client=os.getenv(prefix+'_CLIENT_ID','').strip()
    secret=os.getenv(prefix+'_CLIENT_SECRET','').strip()
    origin=os.getenv('SSO_PUBLIC_ORIGIN','').rstrip('/')
    parsed=urlparse(origin)
    if not client or not secret or parsed.scheme!='https' or not parsed.netloc or parsed.path or parsed.query or parsed.fragment or parsed.username:
        raise SSOError('Este proveedor aún no está configurado')
    return dict(PROVIDERS[provider],client=client,secret=secret,origin=origin,redirect=origin+f'/api/v1/sso/{provider}/callback')

@contextmanager
def db():
    path=Path(os.getenv('SSO_STATE_DB','/state/sso/flows.sqlite3'))
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    connection=sqlite3.connect(path,timeout=10)
    path.chmod(0o600)
    connection.execute('CREATE TABLE IF NOT EXISTS flows (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
    try:
        with connection:
            yield connection
    finally:
        connection.close()

def digest(value): return hashlib.sha256(value.encode()).hexdigest()

def read_flow(connection,flow_id):
    if not re.fullmatch(r'[A-Za-z0-9_-]{32}',flow_id): raise SSOError('Solicitud no válida')
    row=connection.execute('SELECT data FROM flows WHERE id=?',(flow_id,)).fetchone()
    if not row: raise SSOError('Solicitud de acceso no válida o vencida')
    data=json.loads(row[0])
    if data['expires']<time.time(): raise SSOError('Solicitud de acceso vencida')
    return data

def save(connection,flow_id,data):
    connection.execute('INSERT OR REPLACE INTO flows VALUES (?,?)',(flow_id,json.dumps(data)))

def start(provider):
    config=provider_config(provider)
    flow_id=secrets.token_urlsafe(24); proof=secrets.token_urlsafe(32)
    data=dict(provider=provider,proof=digest(proof),state=secrets.token_urlsafe(32),nonce=secrets.token_urlsafe(32),verifier=secrets.token_urlsafe(48),expires=time.time()+300,status='pending')
    with db() as connection:
        connection.execute("DELETE FROM flows WHERE CAST(json_extract(data,'$.expires') AS REAL) < ?",(time.time(),))
        save(connection,flow_id,data)
    return dict(flow_id=flow_id,proof=proof,authorization_url=config['origin']+f'/api/v1/sso/{provider}/authorize?flow_id='+flow_id,expires_in=300)

def authorize(provider,flow_id):
    config=provider_config(provider); cookie=secrets.token_urlsafe(32)
    with db() as connection:
        connection.execute('BEGIN IMMEDIATE')
        data=read_flow(connection,flow_id)
        if data['provider']!=provider or data['status']!='pending': raise SSOError('Solicitud no válida')
        data['cookie']=digest(cookie);save(connection,flow_id,data)
    challenge=base64.urlsafe_b64encode(hashlib.sha256(data['verifier'].encode()).digest()).rstrip(b'=').decode()
    query=dict(client_id=config['client'],redirect_uri=config['redirect'],response_type='code',scope='openid email profile',state=flow_id+'.'+data['state'],nonce=data['nonce'],code_challenge=challenge,code_challenge_method='S256',prompt='select_account')
    return config['authorize']+'?'+urlencode(query),cookie

def verify_identity(provider,id_token,nonce,access_token=None):
    config=provider_config(provider)
    keys=requests.get(config['keys'],timeout=10).json()
    header=jwt.get_unverified_header(id_token)
    if header.get('alg')!='RS256': raise SSOError('Identidad no válida')
    key=next((item for item in keys['keys'] if item['kid']==header.get('kid')),None)
    if key is None: raise SSOError('Identidad no válida')
    claims=jwt.decode(id_token,key,algorithms=['RS256'],audience=config['client'],access_token=access_token,options={'require_exp':True,'require_iat':True,'require_sub':True,'verify_iss':False})
    if claims.get('iss') not in config['issuers'] or not hmac.compare_digest(str(claims.get('nonce','')),nonce): raise SSOError('Identidad no válida')
    if provider=='google' and claims.get('email_verified') is not True: raise SSOError('Correo no verificado por Google')
    if provider=='microsoft' and claims.get('tid')!=MICROSOFT_TENANT: raise SSOError('Se requiere una cuenta personal de Microsoft')
    email=claims.get('email','').strip().lower()
    if '@' not in email: raise SSOError('El proveedor no confirmó un correo electrónico')
    return email

def callback(provider,state,code,cookie):
    flow_id,separator,returned_state=state.partition('.')
    if not separator or not code or not cookie: raise SSOError('Solicitud no válida')
    config=provider_config(provider)
    with db() as connection:
        connection.execute('BEGIN IMMEDIATE')
        data=read_flow(connection,flow_id)
        if data['provider']!=provider or data['status']!='pending' or not hmac.compare_digest(data['state'],returned_state) or not hmac.compare_digest(data.get('cookie',''),digest(cookie)): raise SSOError('Solicitud no válida')
        data['status']='verifying';save(connection,flow_id,data)
    try:
        response=requests.post(config['token'],data=dict(grant_type='authorization_code',client_id=config['client'],client_secret=config['secret'],redirect_uri=config['redirect'],code=code,code_verifier=data['verifier']),timeout=15)
        response.raise_for_status()
        email=verify_identity(provider,response.json()['id_token'],data['nonce'],response.json().get('access_token'))
        mapping=json.loads(os.getenv('SSO_ACCOUNTS_JSON','{}')).get(provider,{})
        username=mapping.get(email)
        if not isinstance(username,str) or not username: raise SSOError('Cuenta no autorizada en SGA-CD')
        data.update(status='ready',username=username,email=email)
    except Exception as error:
        data['status']='denied'
        with db() as connection: save(connection,flow_id,data)
        raise SSOError('No se pudo autorizar esta cuenta en SGA-CD') from error
    for key in ['verifier','nonce','cookie','state']: data.pop(key,None)
    with db() as connection: save(connection,flow_id,data)
    return flow_id

def consume(flow_id,proof,resolve_user):
    with db() as connection:
        connection.execute('BEGIN IMMEDIATE')
        data=read_flow(connection,flow_id)
        if not hmac.compare_digest(data['proof'],digest(proof)): raise SSOError('Solicitud no válida')
        if data['status']=='pending' or data['status']=='verifying': return {'status':'pending'}
        if data['status']!='ready': raise SSOError('La autorización terminó o fue rechazada')
        try:
            result=resolve_user(data['username'],data['email'])
        except SSOError:
            data['status']='denied';save(connection,flow_id,data);connection.commit()
            raise
        data=dict(provider=data['provider'],proof=data['proof'],expires=data['expires'],status='consumed')
        save(connection,flow_id,data)
        return result
