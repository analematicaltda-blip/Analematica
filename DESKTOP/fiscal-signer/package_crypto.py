"""Local interoperability with the browser package protocol; no network/storage."""
import base64,hashlib,hmac,json,os,re
from uuid import UUID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.keywrap import aes_key_wrap,aes_key_unwrap
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
MAX=1024*1024

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def encode(value):return base64.urlsafe_b64encode(value).rstrip(b'=').decode()
def decode(value,size=None,maximum=None):
    if not isinstance(value,str) or len(value)>((maximum or size)*4+2)//3 or not re.fullmatch('[A-Za-z0-9_-]+',value):raise ValueError('Invalid package encoding.')
    result=base64.b64decode(value+'='*((-len(value))%4),altchars=b'-_',validate=True)
    if encode(result)!=value or size is not None and len(result)!=size or maximum is not None and len(result)>maximum:raise ValueError('Invalid package length.')
    return result

def scope(value):
    if not isinstance(value,dict) or set(value)!={'company_id','document_id'} or any(not isinstance(v,str) or str(UUID(v))!=v for v in value.values()):raise ValueError('Explicit canonical scope required.')
    return dict(value)
def derive(password,salt):
    if not isinstance(password,str) or len(password)<16 or len(password.encode())>1024:raise ValueError('Long local password required.')
    def key(s):return PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=s,iterations=600000).derive(password.encode())
    return key(salt),key(salt+b'fiscal-package-auth')
def body(value):return {k:v for k,v in value.items() if k not in {'auth_tag','package_digest'}}

def open_package(value,password,expected):
    expected=scope(expected)
    if not isinstance(value,dict) or set(value)!={'schema','revision','previous_digest','key_descriptor','envelope','auth_tag','package_digest'} or len(canonical(value))>1500000:raise ValueError('Invalid document package.')
    p=json.loads(canonical(value));rev=p['revision']
    if p['schema']!='sgacd-fiscal-package-v1' or type(rev) is not int or not 1<=rev<=1000000 or (rev==1 and p['previous_digest'] is not None) or (rev>1 and (not isinstance(p['previous_digest'],str) or not re.fullmatch('[0-9a-f]{64}',p['previous_digest']))):raise ValueError('Invalid package version.')
    descriptor=p['key_descriptor'];env=p['envelope']
    if not isinstance(descriptor,dict) or set(descriptor)!={'kdf','iterations','salt'} or descriptor['kdf']!='PBKDF2-SHA256' or type(descriptor['iterations']) is not int or descriptor['iterations']!=600000:raise ValueError('Unsupported key derivation.')
    if not isinstance(env,dict) or set(env)!={'schema','algorithm','context','iv','wrapped_key','ciphertext'} or env['schema']!='sgacd-fiscal-envelope-v1' or env['algorithm']!='AES-256-GCM+A256KW' or scope(env['context'])!=expected:raise ValueError('Document scope mismatch.')
    kw,mac=derive(password,decode(descriptor['salt'],16))
    if not isinstance(p['package_digest'],str) or not hmac.compare_digest(hashlib.sha256(canonical({**body(p),'auth_tag':p['auth_tag']})).hexdigest(),p['package_digest']) or not hmac.compare_digest(hmac.digest(mac,canonical(body(p)),'sha256'),decode(p['auth_tag'],32)):raise ValueError('Package authentication failed.')
    dek=aes_key_unwrap(kw,decode(env['wrapped_key'],40));aad=json.dumps([env['schema'],env['algorithm'],expected['company_id'],expected['document_id'],'fiscal-document'],separators=(',',':')).encode();plain=AESGCM(dek).decrypt(decode(env['iv'],12),decode(env['ciphertext'],maximum=MAX+16),aad)
    if not 0<len(plain)<=MAX:raise ValueError('Document outside supported bound.')
    return plain,p

def seal_package(plain,password,expected,revision=1,previous_digest=None):
    expected=scope(expected)
    if not isinstance(plain,bytes) or not 0<len(plain)<=MAX or type(revision) is not int or not 1<=revision<=1000000:raise ValueError('Document or version outside supported bound.')
    if (revision==1 and previous_digest is not None) or (revision>1 and (not isinstance(previous_digest,str) or not re.fullmatch('[0-9a-f]{64}',previous_digest))):raise ValueError('Invalid parent digest.')
    salt=os.urandom(16);kw,mac=derive(password,salt);dek=os.urandom(32);iv=os.urandom(12);aad=json.dumps(['sgacd-fiscal-envelope-v1','AES-256-GCM+A256KW',expected['company_id'],expected['document_id'],'fiscal-document'],separators=(',',':')).encode()
    p={'schema':'sgacd-fiscal-package-v1','revision':revision,'previous_digest':previous_digest,'key_descriptor':{'kdf':'PBKDF2-SHA256','iterations':600000,'salt':encode(salt)},'envelope':{'schema':'sgacd-fiscal-envelope-v1','algorithm':'AES-256-GCM+A256KW','context':expected,'iv':encode(iv),'wrapped_key':encode(aes_key_wrap(kw,dek)),'ciphertext':encode(AESGCM(dek).encrypt(iv,plain,aad))}}
    p['auth_tag']=encode(hmac.digest(mac,canonical(p),'sha256'));p['package_digest']=hashlib.sha256(canonical(p)).hexdigest();return p
